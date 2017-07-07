# -*- coding: utf-8 -*-

# Ported from fribidi-arabic.c - Arabic shaping
#
# Copyright (C) 2005  Behdad Esfahbod
# Copyright (C) 2012  Google, Inc.
#
# This file is based on parts of GNU FriBidi.
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Google Author(s):
#   Behdad Esfahbod

import arabicshapingtab
import joiningtypetab

def do_shaping(t, jtypes, shaper, rtl=True):

	if rtl:
		sprev = 'DL'
		vprev = 1
		snext = 'DR'
		vnext = 2
	else:
		sprev = 'DR'
		vprev = 2
		snext = 'DL'
		vnext = 1

	jprev = 'U'
	length = len (t)
	for i in range (length):
		jthis = jtypes[i]

		j = 1
		jnext = 'U'
		while i + j < length:
			if jtypes[i+j] != 'T':
				jnext = jtypes[i+j]
				break
			j += 1

		shape = 0
		if jprev in sprev:
			shape += vprev
		if jnext in snext:
			shape += vnext

		t[i] = unichr (shaper (ord (t[i]), shape))

		if jthis != 'T':
			jprev = jthis

def do_ligaturing(t, jtypes, table, rtl=True):

	if rtl:
		v0 = 0
		v1 = 1
	else:
		v0 = 1
		v1 = 0
	j = 0;
	length = len (t)
	while j+1 < length:
		pair = (ord(t[j+v0]), ord(t[j+v1]))
		if pair in table:
			t[j] = unichr (table[pair])
			# technically speaking we should fixup jtypes[j], but doesn't matter.
			del t[j+1]
			del jtypes[j+1]
			length -= 1
		j += 1

def arabic_shape(s, pres=True, liga=True, console=True, rtl=True):
	t = list (s)
	jtypes = [joiningtypetab.FRIBIDI_GET_JOINING_TYPE (ord (c)) for c in s]

	if pres:
		do_shaping (t, jtypes, arabicshapingtab.FRIBIDI_GET_ARABIC_SHAPE_PRES, rtl=rtl)
	if liga:
		do_ligaturing (t, jtypes, arabicshapingtab.mandatory_liga_table, rtl=rtl)
	if console:
		do_ligaturing (t, jtypes, arabicshapingtab.console_liga_table, rtl=rtl)
		do_shaping (t, jtypes, arabicshapingtab.FRIBIDI_GET_ARABIC_SHAPE_NSM, rtl=rtl)


	return u''.join (t)
