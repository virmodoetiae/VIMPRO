###############################################################################
##                                                                           ##
##             ________________________________     _________   _________    ##
##            // ____  ____  _________________/    // ____  /  // ____  /    ##
##           // /  // /  // /                     // /  // /  // /  // /     ##
##          // /  // /  // /_____  _________     // /__// /__//_/__// /      ##
##         // /  // /  // ______/ // ______/    // __________________/       ##
##        // /  // /  // /_______//_/_____     // /        // /_____         ##
##       // /  // /  // _______________  /    // /        //_____  /         ##
##      // /  // /  // /_____  // /__// /    // /        ___   // /          ##
##     // /__// /  // ______/ //_______/    // /        // /__// /           ##
##    //_______/  //_/                     //_/        //_______/            ##
##                                                                           ##
##                                                             Stefan Radman ##
###############################################################################

### IMPORTS ###################################################################

import gzip
from PIL import Image

### DATA ######################################################################

# To get the compressed image bytes,
# print(gzip.compress(Image.open("image filename here").convert("RGBA"
#   ).tobytes()))
# Then, copy-paste those within the gzip.decompress method to get the PIL Image

lock_image = Image.frombytes("RGBA", (11,14), 
    gzip.decompress(b'\x1f\x8b\x08\x00\x14n\x92a\x02\xff\xfb\xff\xff?\xc3\xffA\x82\x81\xe0?.L\r\xb5\x84\xc4h\xa1\x16\x9f;G\x12\x06\x00\x8e\x15\xa9\xfbh\x02\x00\x00'))
ulock_image = Image.frombytes("RGBA", (11,14), 
    gzip.decompress(b'\x1f\x8b\x08\x00\xd0n\x92a\x02\xff\xfb\xff\xff?\xc3\x7f \x06\x82\xff\xb8\xf0\x7f\xa8\x9a\xff\x14\xa8%$Fo\xb5\xb80\xb5\xd5\xe2\x0b\xab\x91\x84\x01\x8fl\xc4\x01h\x02\x00\x00'))
icon_image = Image.frombytes("RGBA", (52,52),
    gzip.decompress(b'\x1f\x8b\x08\x00\x1do\x92a\x02\xff\xedY\xcbKrQ\x10\x17B\xcc2\x08\x84 ,j%\xd4\xb2\x9dm\x82\x16A \xd2?\x10\xb4\tW\xe2\xa2\x95\x12a/\xe8EP\x1a\xd9\xcb$\x82\xc4M.\\\x08\nED\x0fiQDE\x7f@Fao\xac\x16\xc2|\xcc\x80\x97\xa3^\xf5\x86\xdaw\xfd\xbe3\xf0\x03\xef\x99\xb9\xe7\xccO\xe7\xce\x9d\x19\x15\n\x05(888888\xfe1\x98\xcdfX^^\x06\x97\xcb\x05\x03\x03\x03\x15\xcbc{{\x1br\xc9\xfc\xfc|EqyyyI\xf3\xff\xed\xed\r>??\xd3\xd6nnn*\x82K0\x18\x14|\x0e\x04\x02i\xba\xaa\xaa*8>>\x16\xf4\x0b\x0b\x0b\xb2\xe6\xa2\xd5j\x05_wvvr\xda\x1d\x1d\x1d\tvr\xe6311!\xd9\xcf\x94\x0c\x0e\x0e\xca\x96O(\x14"\x1f\xcf\xcf\xcf\x0b\xda\xbe\xbe\xbe\x92\xed\xea\xea\xaal\xf9D"\x11\xf2\xf1\xf4\xf4\xb4\xa0\xed\xe3\xe3#\xd9z<\x1e\xd9\xf2\xc1<\xfc\xd3x\xb3Z\xad\xb2\xe5\xa3\xd7\xeb\x05?\xc7\xc6\xc6$\xbd\x9bT*\x95\xacs\xc2\xe5\xe5\xa5\xe0\xab\xc3\xe1\xc8\xd2\xaf\xad\xad\xe5\xcc\xe7rE\xa6\x1c\x1e\x1e\xc2\xc9\xc9I\xda\xda\xf7\xf7wE\xd5\x08WWW9\xeb\x9d\xfd\xfd\xfd\x8a\xac\xe1\xda\xda\xda\xc0\xe9t\xc2\xc1\xc1\x01\xec\xed\xed\xc1\xdc\xdc\x1c455\xf1:\x9d\x83\x83\x83\x83\xe3\xbf\xc3\xf4\xf44\xcd\x03\xee\xee\xee\x8aF,\x16\x83\x8f\x8f\x0f\xda\xf7\xec\xec\x0c\x1e\x1e\x1e\xd2\xf4X\x03566\xc2\xf0\xf00\xf5G\xac\xee\xfd\xfd\x1d,\x16K\xd1|\xd6\xd7\xd7\xa1\xd4\x82\xfb"\x171inn\xa6\xd9\x96\x98 \xcfb\xf9\xac\xac\xac\xd0^___\xb0\xb4\xb4D\xfd$\x02\xd7\xc3\xe1\xb0p\x96\xdb\xed&\xa0\x0ek\xe8\xcd\xcdM\xc1\x96\x05\xf6\n\xb8/~\xe7(\xb7\xb7\xb7\xb0\xb8\xb8H:\x9f\xcf\x07555\xd0\xd7\xd7\x07[[[\xb4\xc6\xf6T6\x9b\xadd|\xee\xef\xef\xe9Z\xa3\xd1@mm-}6\x18\x0c\xc2Y\xd5\xd5\xd5\xa0T*A\xadV\xd3\x1c\x07\xf5uuu\xb4\xce\x02\xd7X>\xe87^\xa7\xf4\r\r\rP__/\\\xb3\xf5z)\xf9`\x7f\xcc\xee=44\x04\x9d\x9d\x9d\xa2qq}}-\xda7\xb0\xf1\x96\xe2\xf3\x13)\'\x1f\x9c\xe3\xe6\xe2\x83\xbdB9\xf8LNN\xfe\x1a\x1f\xccK\x18+:\x9d\x8e\xe2\x05m[[[i\x9dEKKK\x1a\x9f\xdd\xdd]\xea!\xda\xdb\xdb\x05\x88\xdd\x876\x18\xeb\xbf\xc5gjj\x8ar\xfb\xcc\xcc\x0c\xf598\xfb\xc4\xcf,fgg)w\xb1|666\xb2\xce4\x1a\x8d\x94#\xd8{\xb1\x8f\xea\xee\xee\xfe+\xf1&%_\xa7\xf8x\xbd\xde\xbc3\x06V\xc4\xe6\x11\xe5\xe2\xf3\xf4\xf4D\xef@1<??C"\x91\x90\xcc\x07\x7f\xe7d2I\xf7\xc6\xe3\xf1\xb2\xe4\x03<?\x1f\x9fB\xfb\x98L&\xc9|r\xcdWJ\xc9\'S\xf2\xc5[4\x1a\x95\x9c\xdf\xc4\xf8\xe0\xff_\xe5\xca\xd7\xf8\xbe\x13\x13\x9ckvuu\x89\xea...\n\xf2\xc1z\x0c\xc5\xef\xf7K~~FGG\x8b\xe6\xd3\xdb\xdbK\xcf!~7)\xe0\xec\xb3\xa3\xa3\x83r(\xfe\xa7\xc0\xeaFFF\xa0\xbf\xbf\x9f\xee\xc5\x9c\xc7\xea\xecv;\x8c\x8f\x8f\x93\x0ekK\xdc\x07sY\xe6\x99===Yg"\x17\x8c\x07\xde#ppppp\xc8\x11\x7f\x00r\xa2fn@*\x00\x00'))

# To see and modify the images, if needed, save them via the PIL save method
# *_image.save("out.png")

### GAME BOY COLOR SOURCE BOILERPLATES ########################################

# n is the number of palettes, bank1 is a flag to indicate whether the number
# of tiles to be registered in the tileTable is greater than 256, which means
# that bank1 of the tile table should be used as well to store the excess tiles
def fill_from_source_header_to_palettes_start(n, bank1) :
    lines = ""
    lines += ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
    lines += ";;                                                                           ;;\n"
    lines += ";;             _________________________________    _________   _________    ;;\n"
    lines += ";;            // ____  _____  _________________/   // ____  /  // ____  /    ;;\n"
    lines += ";;           // /  // /   // /                    // /  // /  // /  // /     ;;\n"
    lines += ";;          // /  // /   // /____  _________     // /__// /__//_/__// /      ;;\n"
    lines += ";;         // /  // /   // _____/ // ______/    // __________________/       ;;\n"
    lines += ";;        // /  // /   // /______//_/_____     // /        // /_____         ;;\n"
    lines += ";;       // /  // /   // ______________  /    // /        //_____  /         ;;\n"
    lines += ";;      // /  // /   // /____  // /__// /    // /        ___   // /          ;;\n"
    lines += ";;     // /__// /   // _____/ //_______/    // /        // /__// /           ;;\n"
    lines += ";;    //_______/   //_/                    //_/        //_______/            ;;\n"
    lines += ";;                                                                           ;;\n"
    lines += ";;                                                              virmodoetiae ;;\n"
    lines += ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += ";;; EXECUTION ENTRY POINT ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"Header\", ROM0[$0100]\n"
    lines += "    nop\n"
    lines += "    jp Setup\n\n"
    lines += ";;; INTERRUPTS ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"VBlank interrupt\", ROM0[$0040] ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
    lines += "    push hl\n"
    lines += "    ld hl, VBlank\n"
    lines += "    ld [hl], 1\n"
    lines += "    pop hl\n"
    lines += "    reti\n\n"
    lines += ";;; VARIABLES ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"Variables\", WRAM0 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
    lines += "VBlank:\n"
    lines += "    DB\n"
    lines += "tmp:\n"
    lines += "    DB\n\n"
    lines += ";;; MACROS & SUBROUTINES ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"Macros\", ROM0 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "; Load palettes to palette memory\n"
    lines += "    ; 1 -> Palette Index address ($FF68 for background, $FF6A for sprites)\n"
    lines += "    ; 2 -> Address of first palette in list\n"
    lines += "    ; 3 -> Number of palettes to be loaded\n"
    lines += "loadPalettesMacro: MACRO\n"
    lines += "    ld a, %10000000\n"
    lines += "    ld [\\1], a\n"
    lines += "    ld hl, \\2\n"
    lines += "    REPT \\3*8\n"
    lines += "        ld a, [hli]\n"
    lines += "        ld [\\1+1], a\n"
    lines += "    ENDR\n"
    lines += "    ENDM\n\n"
    lines += "SECTION \"Subroutines\", ROM0 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "; Copy data from address de to address hl for\n"
    lines += "; bc times, hl and de are increased at every step.\n"
    lines += "loadAddressInc:\n"
    lines += ".loop\n"
    lines += "    ld a, [de]\n"
    lines += "    ld [hli], a\n"
    lines += "    inc de\n"
    lines += "    dec bc\n"
    lines += "    ld  a, b\n"
    lines += "    or  c\n"
    lines += "    jr  nz, .loop\n"
    lines += "    ret\n\n"
    lines += "; Move tiles starting at address de to addresses starting at hl for bc times\n"
    lines += "; (i.e. for a number bc of tiles). The tiles starting at hl must represent\n"
    lines += "; the visible area of the screen (meaning that screen tiles from x = 20 to\n"
    lines += "; x = 31 are skipped for every line)\n"
    lines += "loadToScreen:\n"
    lines += "    xor a\n"
    lines += "    ld [tmp], a\n"
    lines += ".loop\n"
    lines += "    ld a, [de]\n\n"
    lines += "    ; Wait for VRAM to be accessible before writing to it\n"
    lines += "    push hl\n"
    lines += "    ld hl, $FF41\n"
    lines += ".wait:  \n"
    lines += "    bit  1, [hl]\n"
    lines += "    jr nz, .wait \n"
    lines += "    pop hl\n\n"
    lines += "    ld [hli], a\n"
    lines += "    ld a, [tmp]\n"
    lines += "    cp 20\n"
    lines += "    jr nc, .pass\n"
    lines += "    inc de\n"
    lines += "    dec bc\n"
    lines += "    jr .noReset\n"
    lines += ".pass\n"
    lines += "    cp 31\n"
    lines += "    jr nz, .noReset\n"
    lines += "    ld a, $FF\n"
    lines += "    ld [tmp], a\n"
    lines += ".noReset\n"
    lines += "    inc a\n"
    lines += "    ld [tmp], a\n"
    lines += "    ld  a,b\n"
    lines += "    or  c\n"
    lines += "    jr  nz, .loop\n"
    lines += "    ret\n\n"
    lines += "; Move DMA stored at $28 to $FF80 (i.e. HRAM)\n"
    lines += "copyDMA2HRAM:\n"
    lines += "    ld de, $FF80\n"
    lines += "    ld hl, $28\n"
    lines += "    REPT 10\n"
    lines += "        ld a, [hli]\n"
    lines += "        ld [de], a\n"
    lines += "        inc e\n"
    lines += "    ENDR\n"
    lines += "    ret\n\n"
    lines += "; Wait for any interrupt (halt), if it is a VBlank, return\n"
    lines += "waitVBlank:\n"
    lines += "    halt\n"
    lines += "    nop\n"
    lines += "    ld a, [VBlank]\n"
    lines += "    and a; if a == 0 then z = 0\n"
    lines += "    jr z, waitVBlank\n"
    lines += "    xor a\n"
    lines += "    ret\n\n"
    lines += "; DMA Subroutine that is moved to HRAM by the copyDMA2HRAM subroutine\n"
    lines += "SECTION \"DMA\", ROM0[$28] ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
    lines += "    ld a, $C1\n"
    lines += "    ld [$FF46], a\n"
    lines += "    ld a, $28 ; counting from 40 down lasts circa 160 us\n"
    lines += "wait160us:\n"
    lines += "    dec a\n"
    lines += "    jr nz, wait160us\n"
    lines += "    ret\n\n"
    lines += ";;; MAIN ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"Main\", ROM0[$0150] ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "Setup:\n"
    lines += "    ; Enable VBlank interrupt\n"
    lines += "    ld a, %00000001\n"
    lines += "    ld [$FFFF], a\n"
    lines += "    ei\n\n"
    lines += "    ; Move DMA subroutine to HRAM\n"
    lines += "    call copyDMA2HRAM\n"
    lines += "    ; Write palettes to palette table\n"
    lines += "    call waitVBlank\n"
    lines += "    loadPalettesMacro $FF68, palettesStart, "+str(n)+"\n\n"
    lines += "    ; Reset X,Y screen offsets\n"
    lines += "    xor a\n"
    lines += "    ld [$FF43], a\n"
    lines += "    ld [$FF42], a\n\n"
    lines += "    ; Screen OFF + set FF40 bits :\n"
    lines += "    ; Bit 7 - LCD Display Enable             (0=Off, 1=On)\n"
    lines += "    ; Bit 6 - Window Tile Map Display Select (0=9800-9BFF, 1=9C00-9FFF)\n"
    lines += "    ; Bit 5 - Window Display Enable          (0=Off, 1=On)\n"
    lines += "    ; Bit 4 - BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)\n"
    lines += "    ; Bit 3 - BG Tile Map Display Select     (0=9800-9BFF, 1=9C00-9FFF)\n"
    lines += "    ; Bit 2 - OBJ (Sprite) Size              (0=8x8, 1=8x16)\n"
    lines += "    ; Bit 1 - OBJ (Sprite) Display Enable    (0=Off, 1=On)\n"
    lines += "    ; Bit 0 - BG Display (for CGB see below) (0=Off, 1=On)\n"
    lines += "    ;      76543210\n"
    lines += "    ld a, %00010011\n"
    lines += "    ld [$FF40], a\n\n"
    lines += "    ; Load tiles to bank 0 of tile table\n"
    lines += "    ld hl, $8000\n"
    lines += "    ld de, tileTableBank0Start\n"
    lines += "    ld bc, tileTableBank0End - tileTableBank0Start\n"
    lines += "    call loadAddressInc\n\n"
    if (bank1) :
        lines += "    ; Load tiles to bank 1 of tile table\n"
        lines += "    ld a, 1\n"
        lines += "    ld [$FF4F], a\n"
        lines += "    ld hl, $8000\n"
        lines += "    ld de, tileTableBank1Start\n"
        lines += "    ld bc, tileTableBank1End - tileTableBank1Start\n"
        lines += "    call loadAddressInc\n\n"
    lines += "    ; Draw tiles to screen (bank0 of VRAM)\n"
    lines += "    xor a\n"
    lines += "    ld [$FF4F], a\n"
    lines += "    ld hl, $9800\n"
    lines += "    ld de, tileMapStart\n"
    lines += "    ld bc, tileMapEnd-tileMapStart\n"
    lines += "    call loadToScreen\n\n"
    lines += "    ; Set tiles palette map ( bank1 of VRAM )\n"
    lines += "    ld a, 1\n"
    lines += "    ld [$FF4F], a\n"
    lines += "    ld hl, $9800\n"
    lines += "    ld de, palettesMapStart\n"
    lines += "    ld bc, palettesMapEnd-palettesMapStart\n"
    lines += "    call loadToScreen\n\n"
    lines += "    ; Screen on\n"
    lines += "    ld a, %10010011\n"
    lines += "    ld [$FF40], a\n\n"
    lines += "    ; Lock\n"
    lines += ".loop :\n"
    lines += "    call waitVBlank\n"
    lines += "    halt\n"
    lines += "    nop\n"
    lines += "    jr .loop\n\n"
    lines += ";;; TILE & PALETTE DATA ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "SECTION \"Palettes\", ROM0 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "; Palette colors are in an RGB-555 little-endian format\n"
    lines += "palettesStart:\n"

    return lines

def fill_from_palettes_end_to_bank0_tile_start() :
    lines = ""
    lines += "palettesEnd:\n\n"
    lines += "SECTION \"Tiles\", ROM0 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "tileTableBank0Start:\n"
    return lines

def fill_from_bank0_tile_end_to_bank1_tile_start() :
    lines = ""
    lines += "tileTableBank0End:\n\n"
    lines += "tileTableBank1Start:\n"
    return lines

def fill_from_bank1_tile_end_to_bank0_map_start() :
    lines = ""
    lines += "tileTableBank1End:\n\n"
    lines += "SECTION \"Maps\", ROM0  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n"
    lines += "tileMapStart:\n"
    return lines

def fill_from_bank0_map_end_to_bank1_map_start() :
    lines = ""
    lines += "tileMapEnd:\n\n"
    lines += "palettesMapStart:\n"
    return lines

def fill_from_bank1_map_end_to_source_end() :
    lines = ""
    lines += "palettesMapEnd:\n\n"
    lines += ";;; SOURCE END ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    return lines