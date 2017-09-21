#!/bin/sh

rrdtool graph out.svg \
--imgformat SVG \
--end now \
--start now-7d \
--lower-limit 0 \
--grid-dash 1:0 \
--border 0 \
--color GRID#C0C0C040 \
--color MGRID#A0A0C040 \
--disable-rrdtool-tag \
TEXTALIGN:center \
DEF:am1=rrds/am1.rrd:h:AVERAGE \
DEF:am2=rrds/am2.rrd:h:AVERAGE \
DEF:blen=rrds/blen.rrd:h:AVERAGE \
DEF:giga=rrds/giga.rrd:h:AVERAGE \
DEF:lite=rrds/lite.rrd:h:AVERAGE \
DEF:mega=rrds/mega.rrd:h:AVERAGE \
DEF:nv13=rrds/nv13.rrd:h:AVERAGE \
AREA:am1#183472:_am1:STACK \
AREA:am2#146DB4:_am2:STACK \
AREA:blen#13CAB7:_blen:STACK \
AREA:giga#33C15A:_giga:STACK \
AREA:lite#B8DE4D:_lite:STACK \
AREA:mega#E1EC1C:_mega:STACK \
AREA:nv13#E8B231:_nv13:STACK
#EF7423
#C53C1D
rrdtool graph outl.svg \
--height 200 \
--imgformat SVG \
--end now \
--start now-7d \
--lower-limit 0 \
--grid-dash 1:0 \
--border 0 \
--color GRID#C0C0C040 \
--color MGRID#A0A0C040 \
--disable-rrdtool-tag \
DEF:am1=rrds/am1.rrd:h:AVERAGE \
DEF:am2=rrds/am2.rrd:h:AVERAGE \
DEF:blen=rrds/blen.rrd:h:AVERAGE \
DEF:giga=rrds/giga.rrd:h:AVERAGE \
DEF:lite=rrds/lite.rrd:h:AVERAGE \
DEF:mega=rrds/mega.rrd:h:AVERAGE \
DEF:nv13=rrds/nv13.rrd:h:AVERAGE \
LINE1:am1#FF8F80:am1 \
LINE1:am2#E09040:am2 \
LINE1:blen#DFAF80:blen \
LINE1:giga#C0B040:giga \
LINE1:lite#BFCF80:lite \
LINE1:mega#7FDF80:mega \
LINE1:nv13#A0D040:nv13