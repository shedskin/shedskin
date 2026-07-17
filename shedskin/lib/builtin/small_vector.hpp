#pragma once
//
// small_vector<T, N>
//
// A vector-like container with N elements of inline (stack/member) storage.
// Grows onto the heap only when size exceeds N. Intended for Shedskin's
// generated C++ where many lists/tuples are small and short-lived, so we
// want to avoid a heap allocation + pointer chase in the common case.
//
// Design notes (read before wiring into the codegen):
//  - Verified against the real bdwgc gc_allocator<T> (gc/gc_allocator.h):
//    deallocate() calls GC_FREE unconditionally (not a no-op); construct()
//    only accepts (pointer, const T&), so allocator_traits::construct
//    falls back to placement-new for anything else (emplace_back with
//    non-copy args, default-construct in resize()) -- verified this SFINAE
//    fallback actually fires rather than assuming it. gc_allocator<T>
//    compares equal across all instances and declares no
//    propagate_on_container_* traits, matching the stateless assumptions
//    the move/swap logic below depends on.
//  - GC REACHABILITY HAZARD (found via testing, not specific to this code):
//    the data_ pointer to a heap-spilled buffer is only visible to the
//    collector if whatever memory holds that pointer is itself scanned
//    (stack, static/BSS, or another GC_MALLOC'd block). A small_vector
//    living inside a plain std::allocator-backed container/object (rather
//    than something GC-allocated, e.g. deriving from gc/gc_cleanup) can
//    have its overflow buffer collected while still logically alive, with
//    no compile error -- just silent, load-dependent corruption. Confirm
//    every container Shedskin nests these in is itself GC-reachable.
//  - Heap fallback routes through the Allocator template parameter (default
//    std::allocator<T>) via std::allocator_traits. Pass your libgc-backed
//    allocator as the third template argument; inline storage never touches
//    it at all.
//  - Growth factor is 2x, starting from N. Change next_capacity() if you
//    want a different curve (e.g. 1.5x to reduce peak waste).
//  - Trivially-copyable T (ints, floats, raw pointers) uses memcpy on
//    growth instead of a move-construct loop -- no per-element dispatch,
//    no exception-safety bookkeeping needed.
//  - Exception safety: grow_to() is strongly exception-safe for
//    non-trivial T (rolls back partial construction on throw). If your
//    generated code builds with exceptions disabled, that catch block is
//    dead code and can be stripped -- flag if that's the case.
//  - Only single-buffer swap between two heap-allocated instances is O(1);
//    swap() involving inline storage falls back to move-construct, which is
//    O(N) but still avoids heap traffic.

#include <cstddef>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <initializer_list>

namespace ss {

// Allocator is expected to satisfy the standard Allocator named requirement
// (allocate/deallocate at minimum; construct/destroy optional and defaulted
// by std::allocator_traits if not provided). Verified against the real
// bdwgc gc_allocator<T>: its deallocate() calls GC_FREE unconditionally --
// this is a normal allocate/deallocate pairing, not a "let the collector
// handle it" no-op, which matters if you ever swap in a different allocator.
//
// Inline (<=N element) storage NEVER goes through the allocator -- it's a
// plain member array, scanned conservatively by libgc as part of whatever
// object owns the small_vector. Only heap fallback uses Allocator.
template <typename T, std::size_t N, typename Allocator = std::allocator<T>>
class small_vector : private Allocator {
    static_assert(N > 0, "small_vector inline capacity must be > 0");

    using alloc_traits = std::allocator_traits<Allocator>;
    static_assert(std::is_same<typename alloc_traits::value_type, T>::value,
                  "Allocator::value_type must match T");

public:
    using value_type      = T;
    using size_type       = std::size_t;
    using reference       = T&;
    using const_reference = const T&;
    using iterator        = T*;
    using const_iterator   = const T*;
    using allocator_type  = Allocator;

    small_vector() noexcept(std::is_nothrow_default_constructible<Allocator>::value)
        : Allocator(), data_(inline_ptr()), size_(0), capacity_(N) {}

    explicit small_vector(const Allocator& alloc) noexcept
        : Allocator(alloc), data_(inline_ptr()), size_(0), capacity_(N) {}

    explicit small_vector(size_type count, const Allocator& alloc = Allocator())
        : small_vector(alloc) {
        resize(count);
    }

    small_vector(std::initializer_list<T> init, const Allocator& alloc = Allocator())
        : small_vector(alloc) {
        reserve(init.size());
        for (const auto& v : init) emplace_back(v);
    }

    small_vector(const small_vector& other)
        : Allocator(alloc_traits::select_on_container_copy_construction(other.get_alloc())),
          data_(inline_ptr()), size_(0), capacity_(N) {
        reserve(other.size_);
        uninitialized_copy_n(data_, other.data_, other.size_);
        size_ = other.size_;
    }

    // Allocator is copied from other (standard move-ctor behavior). Safe to
    // always steal the buffer pointer here since `this`'s allocator is a
    // copy of the one that allocated it.
    small_vector(small_vector&& other) noexcept(std::is_nothrow_move_constructible<T>::value)
        : Allocator(other.get_alloc()) {
        move_buffer_from(std::move(other));
    }

    small_vector& operator=(const small_vector& other) {
        if (this == &other) return *this;

        if constexpr (alloc_traits::propagate_on_container_copy_assignment::value) {
            if (get_alloc() != other.get_alloc()) {
                // Our buffer was allocated with an allocator we're about to
                // replace -- must release it under the OLD allocator first.
                destroy_all();
                free_heap();
                get_alloc() = other.get_alloc();
                data_ = inline_ptr();
                size_ = 0;
                capacity_ = N;
                reserve(other.size_);
                uninitialized_copy_n(data_, other.data_, other.size_);
                size_ = other.size_;
                return *this;
            }
            get_alloc() = other.get_alloc();
        }

        if (other.size_ <= capacity_) {
            // Common case: reuse existing storage instead of reallocating.
            // This is the path that matters for "assign fresh contents into
            // an already-sized vector in a loop" -- reallocating here every
            // time (as a naive copy-and-swap would) is the single biggest
            // performance gap vs std::vector for large vectors.
            if constexpr (std::is_trivially_copyable_v<T>) {
                if (other.size_) std::memcpy(data_, other.data_, other.size_ * sizeof(T));
            } else {
                size_type common = other.size_ < size_ ? other.size_ : size_;
                for (size_type i = 0; i < common; ++i) data_[i] = other.data_[i];
                if (other.size_ > size_) {
                    for (size_type i = size_; i < other.size_; ++i)
                        alloc_traits::construct(get_alloc(), data_ + i, other.data_[i]);
                } else {
                    for (size_type i = other.size_; i < size_; ++i)
                        alloc_traits::destroy(get_alloc(), data_ + i);
                }
            }
            size_ = other.size_;
            return *this;
        }

        // Insufficient capacity: must allocate. Build directly into a fresh
        // buffer sized to other.size_ (strongly exception-safe: `this` is
        // untouched if the copy throws), rather than routing through a
        // temporary + swap, which costs an extra move pass for no benefit
        // once we're already forced to allocate.
        T* new_data = alloc_traits::allocate(get_alloc(), other.size_);
        try {
            uninitialized_copy_n(new_data, other.data_, other.size_);
        } catch (...) {
            alloc_traits::deallocate(get_alloc(), new_data, other.size_);
            throw;
        }
        destroy_all();
        free_heap();
        data_ = new_data;
        size_ = other.size_;
        capacity_ = other.size_;
        return *this;
    }

    small_vector& operator=(small_vector&& other) noexcept(std::is_nothrow_move_constructible<T>::value) {
        if (this == &other) return *this;
        destroy_all();
        if (alloc_traits::propagate_on_container_move_assignment::value) {
            free_heap();
            get_alloc() = other.get_alloc();
            move_buffer_from(std::move(other));
        } else if (get_alloc() == other.get_alloc()) {
            free_heap();
            move_buffer_from(std::move(other));
        } else {
            // Allocators differ and don't propagate: must move element-wise
            // using OUR allocator; can't adopt a buffer freed by a
            // different allocator instance.
            size_ = 0; // destroy_all() already ran; data_/capacity_ still valid to reuse
            reserve(other.size_);
            for (size_type i = 0; i < other.size_; ++i)
                emplace_back(std::move(other.data_[i]));
            other.clear();
        }
        return *this;
    }

    ~small_vector() {
        destroy_all();
        free_heap();
    }

    allocator_type get_allocator() const { return get_alloc(); }

    // -- element access --------------------------------------------------
    reference       operator[](size_type i)       { return data_[i]; }
    const_reference operator[](size_type i) const { return data_[i]; }

    reference at(size_type i) {
        if (i >= size_) throw std::out_of_range("small_vector::at");
        return data_[i];
    }
    const_reference at(size_type i) const {
        if (i >= size_) throw std::out_of_range("small_vector::at");
        return data_[i];
    }

    reference front()             { return data_[0]; }
    const_reference front() const { return data_[0]; }
    reference back()              { return data_[size_ - 1]; }
    const_reference back() const  { return data_[size_ - 1]; }

    T*       data()       noexcept { return data_; }
    const T* data() const noexcept { return data_; }

    // -- iterators --------------------------------------------------------
    iterator       begin()       noexcept { return data_; }
    iterator       end()         noexcept { return data_ + size_; }
    const_iterator begin() const noexcept { return data_; }
    const_iterator end()   const noexcept { return data_ + size_; }
    const_iterator cbegin() const noexcept { return data_; }
    const_iterator cend()   const noexcept { return data_ + size_; }

    // -- capacity -----------------------------------------------------------
    size_type size() const noexcept     { return size_; }
    size_type capacity() const noexcept { return capacity_; }
    bool empty() const noexcept         { return size_ == 0; }
    bool is_inline() const noexcept     { return data_ == inline_ptr(); }

    void reserve(size_type new_cap) {
        if (new_cap <= capacity_) return;
        grow_to(new_cap);
    }

    // -- modifiers ------------------------------------------------------
    void push_back(const T& v) { emplace_back(v); }
    void push_back(T&& v)      { emplace_back(std::move(v)); }

    template <typename... Args>
    reference emplace_back(Args&&... args) {
        if (size_ == capacity_) grow_to(next_capacity());
        alloc_traits::construct(get_alloc(), data_ + size_, std::forward<Args>(args)...);
        ++size_;
        return data_[size_ - 1];
    }

    void pop_back() {
        --size_;
        alloc_traits::destroy(get_alloc(), data_ + size_);
    }

    void clear() noexcept {
        destroy_all();
        size_ = 0;
    }

    void resize(size_type count) {
        if (count < size_) {
            for (size_type i = count; i < size_; ++i)
                alloc_traits::destroy(get_alloc(), data_ + i);
            size_ = count;
        } else if (count > size_) {
            reserve(count);
            for (size_type i = size_; i < count; ++i)
                alloc_traits::construct(get_alloc(), data_ + i);
            size_ = count;
        }
    }

    void swap(small_vector& other) noexcept(std::is_nothrow_move_constructible<T>::value) {
        // Cheap path: both on the heap, and it's safe to swap raw pointers
        // -- either the allocator propagates on swap, or the two allocator
        // instances are equal so either one can free either buffer.
        bool can_steal_pointers = !is_inline() && !other.is_inline() &&
            (alloc_traits::propagate_on_container_swap::value || get_alloc() == other.get_alloc());
        if (can_steal_pointers) {
            std::swap(data_, other.data_);
            std::swap(size_, other.size_);
            std::swap(capacity_, other.capacity_);
            if (alloc_traits::propagate_on_container_swap::value) {
                using std::swap;
                swap(get_alloc(), other.get_alloc());
            }
            return;
        }
        // Otherwise: inline storage involved, or heap buffers whose
        // allocators aren't interchangeable. Fall back to move-through-temp,
        // which routes through operator=(&&) and therefore already handles
        // the unequal-allocator case correctly (element-wise move).
        small_vector tmp(std::move(*this));
        *this = std::move(other);
        other = std::move(tmp);
    }

private:
    // Copies n elements from src into raw (uninitialized) memory at dst.
    // memcpy fast path for trivially-copyable T avoids the per-element
    // construct()-with-capacity-check overhead that a naive emplace_back
    // loop has even after reserve() -- that check can't be optimized away
    // by the compiler in general, and blocks it collapsing into a single
    // bulk copy. Exception-safe for non-trivial T: rolls back partial
    // construction on throw, same discipline as grow_to().
    void uninitialized_copy_n(T* dst, const T* src, size_type n) {
        if constexpr (std::is_trivially_copyable_v<T>) {
            if (n) std::memcpy(dst, src, n * sizeof(T));
        } else {
            size_type i = 0;
            try {
                for (; i < n; ++i) alloc_traits::construct(get_alloc(), dst + i, src[i]);
            } catch (...) {
                for (size_type j = 0; j < i; ++j) alloc_traits::destroy(get_alloc(), dst + j);
                throw;
            }
        }
    }

    Allocator& get_alloc() noexcept { return *this; }
    const Allocator& get_alloc() const noexcept { return *this; }

    T* inline_ptr() noexcept { return reinterpret_cast<T*>(inline_storage_); }
    const T* inline_ptr() const noexcept { return reinterpret_cast<const T*>(inline_storage_); }

    size_type next_capacity() const {
        return capacity_ * 2; // capacity_ is always >= N, never 0
    }

    void grow_to(size_type new_cap) {
        T* new_data = alloc_traits::allocate(get_alloc(), new_cap);

        if constexpr (std::is_trivially_copyable_v<T>) {
            // Bypasses construct()/destroy() -- assumes the allocator
            // doesn't customize construction for trivially-copyable T.
            // True for std::allocator and for a plain GC_malloc wrapper;
            // flag if your allocator ever needs to intercept this.
            std::memcpy(new_data, data_, size_ * sizeof(T));
        } else {
            size_type i = 0;
            try {
                for (; i < size_; ++i)
                    alloc_traits::construct(get_alloc(), new_data + i, std::move_if_noexcept(data_[i]));
            } catch (...) {
                for (size_type j = 0; j < i; ++j) alloc_traits::destroy(get_alloc(), new_data + j);
                alloc_traits::deallocate(get_alloc(), new_data, new_cap);
                throw;
            }
            destroy_all();
        }

        free_heap();
        data_ = new_data;
        capacity_ = new_cap;
    }

    void destroy_all() noexcept {
        for (size_type i = 0; i < size_; ++i)
            alloc_traits::destroy(get_alloc(), data_ + i);
    }

    void free_heap() noexcept {
        if (!is_inline()) alloc_traits::deallocate(get_alloc(), data_, capacity_);
    }

    // Transfers the buffer/size/capacity only -- does NOT touch the
    // allocator. Caller is responsible for having already made sure it's
    // safe for `this`'s allocator to own whatever buffer ends up here
    // (either because it was just constructed from other's allocator, or
    // because the allocators are known to compare equal / propagate).
    void move_buffer_from(small_vector&& other) noexcept(std::is_nothrow_move_constructible<T>::value) {
        if (other.is_inline()) {
            data_ = inline_ptr();
            capacity_ = N;
            for (size_type i = 0; i < other.size_; ++i)
                alloc_traits::construct(get_alloc(), data_ + i, std::move(other.data_[i]));
            size_ = other.size_;
            other.clear();
        } else {
            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;
            other.data_ = other.inline_ptr();
            other.size_ = 0;
            other.capacity_ = N;
        }
    }

    alignas(T) unsigned char inline_storage_[N * sizeof(T)];
    T* data_;
    size_type size_;
    size_type capacity_;
};

} // namespace ss
