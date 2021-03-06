from PIL import Image, ImageDraw, ImageFont
import math
import random
from Config import (WIDTH,
                    HEIGHT_WITHOUT_MAPPINGS,
                    OFFSET,
                    OFFSET_TOP,
                    OFFSET_MAPPINGS,
                    MAPPING_WIDTH,
                    MAPPPING_COLOUR,
                    MAPPPING_COLOUR_READ,
                    LINEWIDTH,
                    FEATUREWIDTH,
                    FONTSIZE,
                    ARROW_OFFSET,
                    FONT,
                    BLAST_FEATURE_MAPPING,
                    COLOURS)

def draw_feature(draw, font, hit_dict, contig_length, top):
    x1 = math.floor((WIDTH-2*OFFSET) * hit_dict["qstart"] / contig_length)+OFFSET
    x2 = math.ceil((WIDTH-2*OFFSET) * hit_dict["qend"] / contig_length)+OFFSET
    y_line = OFFSET_TOP

    label = hit_dict["hitname"]+":\n"+str(hit_dict["sstart"])+"-"+str(hit_dict["send"])
    (textsize_x, textsize_y) = draw.multiline_textsize(label, font=font)
    x_text = int((x2+x1-textsize_x)/2)
    if top:
        y_text = y_line-FEATUREWIDTH-textsize_y
    else:
        y_text = y_line+FEATUREWIDTH
    draw.multiline_text((x_text,y_text), label, font=font, fill=COLOURS[hit_dict["f_type"]], align="center")

    if(hit_dict["sstart"] < hit_dict["send"]):
        p1 = (x1, y_line-1/2*FEATUREWIDTH)
        p2 = (x1+ARROW_OFFSET, y_line)    
        p3 = (x1, y_line+1/2*FEATUREWIDTH)
        p4 = (x2-ARROW_OFFSET, y_line+1/2*FEATUREWIDTH)
        p5 = (x2, y_line)
        p6 = (x2-ARROW_OFFSET, y_line-1/2*FEATUREWIDTH)
    else:
        p1 = (x1+ARROW_OFFSET, y_line-1/2*FEATUREWIDTH)
        p2 = (x1, y_line)    
        p3 = (x1+ARROW_OFFSET, y_line+1/2*FEATUREWIDTH)
        p4 = (x2, y_line+1/2*FEATUREWIDTH)
        p5 = (x2-ARROW_OFFSET, y_line)
        p6 = (x2, y_line-1/2*FEATUREWIDTH)
    polygon = [p1, p2, p3, p4, p5, p6]
    draw.polygon(polygon, fill=COLOURS[hit_dict["f_type"]])

def draw_arrow(draw, y, x_start, x_end, width, colour):
    if(x_start < x_end):
        p1 = (x_start, y-1/2*width)
        p2 = (x_start+ARROW_OFFSET, y)    
        p3 = (x_start, y+1/2*width)
        p4 = (x_end-ARROW_OFFSET, y+1/2*width)
        p5 = (x_end, y)
        p6 = (x_end-ARROW_OFFSET, y-1/2*width)
    else:
        p1 = (x_start+ARROW_OFFSET, y-1/2*width)
        p2 = (x_start, y)    
        p3 = (x_start+ARROW_OFFSET, y+1/2*width)
        p4 = (x_end, y+1/2*width)
        p5 = (x_end-ARROW_OFFSET, y)
        p6 = (x_end, y-1/2*width)    
    polygon = [p1, p2, p3, p4, p5, p6]
    draw.polygon(polygon, fill=colour)

def random_colour():
    levels = range(0,192,12)
    return tuple(random.choice(levels) for _ in range(3))

def draw_mapping(draw, y, read, qstart, qend, sstart, send, read_length, contig_length, colour=None):
    if(sstart < send):
        read_start = sstart-qstart
        read_end = send+(read_length-qend)
    else:
        read_start = sstart+qstart
        read_end = send-(read_length-qend)
    
    x1 = math.floor((WIDTH-2*OFFSET) * sstart / contig_length)+OFFSET
    x2 = math.ceil((WIDTH-2*OFFSET) * send / contig_length)+OFFSET
    x1_read = math.floor((WIDTH-2*OFFSET) * read_start / contig_length)+OFFSET
    x2_read = math.ceil((WIDTH-2*OFFSET) * read_end / contig_length)+OFFSET
    draw_arrow(draw, y, x1_read, x2_read, MAPPING_WIDTH, MAPPPING_COLOUR_READ)
    if colour is None:
        draw_arrow(draw, y, x1, x2, MAPPING_WIDTH, MAPPPING_COLOUR)
    else:
        draw_arrow(draw, y, x1, x2, MAPPING_WIDTH, colour)
    

def draw_mappings(draw, mappings, contig_length):
    y = OFFSET_MAPPINGS
    mapping_length_dict = {}
    for read in mappings:
        mapping_length_dict[read] = mappings[read]["max_mapping_length"]
    sorted_reads = sorted(mapping_length_dict.items(), key = lambda x: x[1], reverse=True)
    
    for read_tupel in sorted_reads:
        y += MAPPING_WIDTH
        read = read_tupel[0]
        read_length = mappings[read]["length"]
        read_hits = mappings[read]["hits"]
        #rand_colour = random_colour()
        for hit in read_hits:
            y += 2*MAPPING_WIDTH
            draw_mapping(draw, y, read, int(hit["qstart"]), int(hit["qend"]), int(hit["sstart"]), int(hit["send"]), read_length, contig_length)

        
def draw_insertion(image_name, contig_dict, mappings):
    number_hits = 0
    if(mappings is not None):
        for read in mappings:
            for hit in mappings[read]["hits"]:
                number_hits += 1
    height =  HEIGHT_WITHOUT_MAPPINGS+MAPPING_WIDTH*2*number_hits+50
        
    im = Image.new("RGB", (WIDTH, height), (255,255,255))
    contig_length = int(contig_dict["length"])
    blast_hits = contig_dict["hits"]
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, FONTSIZE)
    y = OFFSET_TOP
    draw.line((0+OFFSET, y, WIDTH-OFFSET, y), width=LINEWIDTH, fill=(0,0,0))
    #create feature dicr:
    top = False;
    for hit in sorted(blast_hits, key = lambda i: i["qstart"]):
        hit_dict = {"hitname": hit["saccver"], 
                    "qstart": int(hit["qstart"]), 
                    "qend": int(hit["qend"]), 
                    "sstart": int(hit["sstart"]), 
                    "send": int(hit["send"]), 
                    "f_type": BLAST_FEATURE_MAPPING[hit["saccver"]] if (hit["saccver"] in BLAST_FEATURE_MAPPING) else "other"
                    }
        draw_feature(draw, font, hit_dict, contig_length, top)
        top = not top;

    if(mappings is not None):        
        draw_mappings(draw, mappings, contig_length)
    
    im.save(image_name, "PNG")



