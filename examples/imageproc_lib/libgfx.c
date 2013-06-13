/*
 *       C image processing example
 *
 *       Paul Haeberli
 */
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define SHIFT_R (0*8)
#define SHIFT_G (1*8)
#define SHIFT_B (2*8)
#define SHIFT_A (3*8)

#define RVAL(pix32) ((int)(((pix32)>>SHIFT_R)&0xff))
#define GVAL(pix32) ((int)(((pix32)>>SHIFT_G)&0xff))
#define BVAL(pix32) ((int)(((pix32)>>SHIFT_B)&0xff))
#define AVAL(pix32) ((int)(((pix32)>>SHIFT_A)&0xff))

#define CPACK(r,g,b,a)  (((r)<<SHIFT_R) | ((g)<<SHIFT_G) | ((b)<<SHIFT_B) | ((a)<<SHIFT_A))

#define RINTLUM         (57)
#define GINTLUM         (179)
#define BINTLUM         (20)

#define ILUM(r,g,b)     ((int)(RINTLUM*(r)+GINTLUM*(g)+BINTLUM*(b))>>8)

typedef struct canvas {
    int sizex;
    int sizey;
    unsigned int *data;
} canvas;

static int nalloc = 0;

canvas *cannew(int sizex, int sizey)
{
    canvas *c;

    c = (canvas *)malloc(sizeof(canvas));
    c->sizex = sizex;
    c->sizey = sizey;
    c->data = (unsigned int *)malloc(sizex*sizey*sizeof(unsigned int));
    nalloc++;
    return c;
}

int infree = 0;

void canfree(canvas *c)
{
    infree++;
    fprintf(stderr, "    CANFREE called\n");
    if(infree == 2) {
	fprintf(stderr, "    ERROR: grr... canfree called from multiple threads\n");
	exit(1);
    }
    if(!c) {
        infree--;
	return;
    }
    free(c->data);
    free(c);
    nalloc--;
    infree--;
}

int cannalloc()
{
    return nalloc;
}

canvas *canclone(canvas *c)
{
    canvas *cc;

    cc = cannew(c->sizex,c->sizey);
    memcpy((void *)cc->data, (void *)c->data, c->sizex*c->sizey*sizeof(unsigned int));
    return cc;
}

void cansize(canvas *c, int *sizex, int *sizey)
{
    *sizex = c->sizex;
    *sizey = c->sizex;
}
 
static int limit(int val, int min, int max)
{
    if(val<min)
	return min;
    if(val>max)
	return max;
    return val;
}

static int pixlerp(int v0, int v1, float a)
{
    return limit(round(v0*(1.0-a) + v1*a), 0, 255);
}

void cansaturate(canvas *c, float sat)
{
    int npix = c->sizex*c->sizey;
    unsigned int *lptr = c->data;
    while(npix--) {
	int r = RVAL(*lptr);
	int g = GVAL(*lptr);
	int b = BVAL(*lptr);
	int lum = ILUM(r,g,b);
	*lptr++ = CPACK(pixlerp(lum,r,sat),pixlerp(lum,g,sat),pixlerp(lum,b,sat),255);
    }
}

void canclear(canvas *c, float r, float g, float b, float a)
{
    int ir = round(255*r);
    int ig = round(255*g);
    int ib = round(255*b);
    int ia = round(255*a);
    unsigned int color = CPACK(ir, ig, ib, ia);

    int npix = c->sizex*c->sizey;
    unsigned int *lptr = c->data;
    while(npix--)
	*lptr++ = color;
}

void canscalergba(canvas *c, float r, float g, float b, float a)
{
    int npix = c->sizex*c->sizey;
    unsigned int *lptr = c->data;
    while(npix--) {
	int ir = round(r*RVAL(*lptr));
	int ig = round(g*GVAL(*lptr));
	int ib = round(b*BVAL(*lptr));
	int ia = round(a*AVAL(*lptr));
	*lptr++ = CPACK(ir,ig,ib,ia);
    }
}

unsigned int cangetpix(canvas *c, int x, int y)
{
    if((x<0) || (x>=c->sizex))
	return CPACK(0,0,0,0);
    if((y<0) || (y>=c->sizey))
	return CPACK(0,0,0,0);
    return c->data[y*c->sizex+x];
}

unsigned int canputpix(canvas *c, int x, int y, int pix)
{
    x = limit(x, 0, c->sizex-1);
    y = limit(y, 0, c->sizey-1);
    c->data[y*c->sizex+x] = pix;
}

canvas *canshift(canvas *c, int shiftx, int shifty)
{
    int x, y;
    canvas *out = canclone(c);
    int sizex = out->sizex;
    int sizey = out->sizey;
    unsigned int *optr = out->data;
    for(y=0; y<sizey; y++) {
	for(x=0; x<sizex; x++)
	    *optr++ = cangetpix(c, x-shiftx, y-shifty);
    }
    return out;
}

canvas *canframe(canvas *c, float r, float g, float b, float a, int width)
{
    int x, y;
    canvas *out = cannew(c->sizex+2*width, c->sizey+2*width);
    canclear(out, r, g, b, a);
    int sizex = c->sizex;
    int sizey = c->sizey;
    unsigned int *lptr = c->data;
    for(y=0; y<sizey; y++) {
        for(x=0; x<sizex; x++)
	    canputpix(out, x+width, y+width, cangetpix(c,x,y));
    }
    return out;
}

static int cansizecheck(canvas *c1, canvas *c2, const char *str)
{
    if((c1->sizex != c2->sizex) || (c1->sizey != c2->sizey)) {
        fprintf(stderr,"    Error: cansizecheck [%s] failed!\n",str);
        fprintf(stderr,"    can1: %d by %d\n",c1->sizex,c1->sizey);
        fprintf(stderr,"    can2: %d by %d\n",c2->sizex,c2->sizey);
        return 0;
    }
    return 1;
}

void canmult(canvas *a, canvas *b)
{
    if(!cansizecheck(a, b, "canmult: canvases must be the same size\n"))
        return;
    int npix = a->sizex*a->sizey;
    unsigned int *aptr = a->data;
    unsigned int *bptr = b->data;
    while(npix--) {
        int ir = round(RVAL(*aptr)*RVAL(*bptr)/255.0);
        int ig = round(GVAL(*aptr)*GVAL(*bptr)/255.0);
        int ib = round(BVAL(*aptr)*BVAL(*bptr)/255.0);
        int ia = round(AVAL(*aptr)*AVAL(*bptr)/255.0);
        *aptr = CPACK(ir,ig,ib,ia);
        aptr++;
        bptr++;
    }
}

void canblend(canvas *dst, canvas *src, float fr, float fg, float fb, float fa)
{
    if(!cansizecheck(dst, src, "canmult: canvases must be the same size\n"))
        return;
    unsigned int *dptr = dst->data;
    unsigned int *sptr = src->data;
    int npix = dst->sizex*dst->sizey;
    while(npix--) {
        float fas = fa*AVAL(*sptr)/255.0;
        int rd = round(fr*RVAL(*sptr) + (1.0-fas)*RVAL(*dptr));
        int gd = round(fg*GVAL(*sptr) + (1.0-fas)*GVAL(*dptr));
        int bd = round(fb*BVAL(*sptr) + (1.0-fas)*BVAL(*dptr));
        int ad = round(fa*AVAL(*sptr) + (1.0-fas)*AVAL(*dptr));
        *dptr++ = CPACK(rd, gd, bd, ad);
        sptr++;
    }
}

canvas *cansubimg(canvas *c, int orgx, int orgy, int sizex, int sizey)
{
    int x, y;
    canvas *out = cannew(sizex, sizey);
    unsigned int *lptr = out->data;
    for(y=0; y<sizey; y++) {
        for(x=0; x<sizex; x++)
	   *lptr++ = cangetpix(c, orgx+x, orgy+y);
    }
    return out;
}

/* point sampled zoom for this example */

canvas *canzoom(canvas *c, float zoomx, float zoomy)
{
    int x, y;
    int sizex = round(c->sizex*zoomx);
    if (sizex<1) sizex = 1;
    int sizey = round(c->sizey*zoomy);
    if (sizey<1) sizey = 1;

    canvas *out = cannew(sizex, sizey);
    unsigned int *lptr = out->data;

    for(y=0; y<sizey; y++) {
        float py = (y+0.5)/sizey;
        int sy = py*c->sizey;
        for(x=0; x<sizex; x++) {
	   float px = (x+0.5)/sizex;
	   int sx = px*c->sizex;
	   *lptr++ = cangetpix(c, sx, sy);
	}
    }
    return out;
}

// TGA support for this example 

int cantofile(canvas *c, const char *outfilename)
{
    FILE *fptr = fopen(outfilename, "wb");
    if(!fptr) {
	fprintf(stderr, "    Error: cantofile: can't open output file\n");
	fprintf(stderr, "    [%s]\n",outfilename);
	return 0;
    }
    int sizex = c->sizex;
    int sizey = c->sizey;
    
    // from http://paulbourke.net/dataformats/tga/

    putc(0,fptr);
    putc(0,fptr);
    putc(2,fptr);                         /* uncompressed RGB */
    putc(0,fptr); putc(0,fptr);
    putc(0,fptr); putc(0,fptr);
    putc(0,fptr);
    putc(0,fptr); putc(0,fptr);           /* X origin */
    putc(0,fptr); putc(0,fptr);           /* y origin */
    putc((sizex & 0x00FF),fptr);
    putc((sizex & 0xFF00) / 256,fptr);
    putc((sizey & 0x00FF),fptr);
    putc((sizey & 0xFF00) / 256,fptr);
    putc(32,fptr);                        /* 32 bit bitmap */
    putc(0,fptr);

    for(int y=0; y<sizey; y++) {
        unsigned int *lptr = c->data+((sizey-1-y)*sizex);
        for(int x=0; x<sizex; x++) {
            putc(BVAL(*lptr),fptr);
            putc(GVAL(*lptr),fptr);
            putc(RVAL(*lptr),fptr);
            putc(AVAL(*lptr),fptr);
	    lptr++;
        }
    }
    fclose(fptr);
    return 1;
}

static int fgetint(FILE *fptr)
{
    int low = fgetc(fptr);
    int hi = fgetc(fptr);
    int val = (hi<<8)+low;
    if(val>4096) {
	fprintf(stderr, "    Error: canfromfile: strange int val: %d\n", val);
	return 4096;
    }
    return val;
}

canvas *canfromfile(const char *infilename)
{
    int i;
    FILE *fptr = fopen(infilename, "rb");
    if(!fptr) {
	fprintf(stderr, "    Error: canfromfile: can't open input file\n");
	fprintf(stderr, "    [%s]\n",infilename);
	return 0;
    }
    fgetc(fptr);
    fgetc(fptr);
    int imagetype =  fgetc(fptr);    
    if(imagetype != 2) {
	fprintf(stderr, "    Error: canfromfile: strange imagetype %d\n", imagetype);
	exit(1);
    }
    for(i=0; i<9; i++)
        fgetc(fptr);
    int sizex = fgetint(fptr);
    int sizey = fgetint(fptr);
    int imagebits =  fgetc(fptr);    
    if( (imagebits != 32) && (imagebits != 24)) {
	fprintf(stderr, "    Error: canfromfile: strange imagebits %d\n", imagebits);
	exit(1);
    }
    fgetc(fptr);

    canvas *c = cannew(sizex, sizey);
    if(imagebits == 32) {
        for(int y=0; y<sizey; y++) {
            unsigned int *lptr = c->data+((sizey-1-y)*sizex);
            for(int x=0; x<sizex; x++) {
	        int ib = fgetc(fptr);
	        int ig = fgetc(fptr);
	        int ir = fgetc(fptr);
	        int ia = fgetc(fptr);
	        *lptr++ = CPACK(ir, ig, ib, ia);
	    }
        }
    } else {
        for(int y=0; y<sizey; y++) {
            unsigned int *lptr = c->data+((sizey-1-y)*sizex);
            for(int x=0; x<sizex; x++) {
	        int ib = fgetc(fptr);
	        int ig = fgetc(fptr);
	        int ir = fgetc(fptr);
	        int ia = 255;
	        *lptr++ = CPACK(ir, ig, ib, ia);
	    }
	}
    }
    fclose(fptr);
    return c;
}

