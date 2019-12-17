import json, nltk, spacy, argparse
from trec_car.read_data import *

# Not including such articles whose name has a '/' character. It causes issue while parsing page IDs
# from hierarchical qrels

def read_art_qrels(art_qrels_file):
    art_dict = dict()
    with open(art_qrels_file, 'r') as a:
        for l in a:
            q = l.split(' ')[0]
            if '/' in q:
                continue
            p = l.split(' ')[2]
            if q in art_dict.keys():
                art_dict[q].append(p)
            else:
                art_dict[q] = [p]
    return art_dict

# If there are duplicate paras in an article, meaning same para appears in more than one section in an
# article, then the reverse hier qrels dict maps those paras to a single section. This deduplication
# strategy makes sense because if a para appears in both the section then paras from either section are
# similar to this para

def read_rev_hier_qrels(hier_qrels_file, art_dict):
    page_ids = art_dict.keys()
    rev_hier_dict = dict()
    with open(hier_qrels_file, 'r') as a:
        for l in a:
            q = l.split(' ')[0]
            page = q.split('/')[0]
            if page not in page_ids:
                continue
            sec = page
            if '/' in q:
                sec = ' '.join([q.split('/')[i] for i in range(1, len(q.split('/')))])
            para = l.split(' ')[2]
            if page not in rev_hier_dict.keys():
                rev_hier_dict[page] = dict()
            rev_hier_dict[page][para] = sec
    return rev_hier_dict

def generate_parapair(art_qrels, top_qrels, hier_qrels, output_file):
    art_dict = read_art_qrels(art_qrels)
    top_dict = read_rev_hier_qrels(top_qrels, art_dict)
    hier_dict = read_rev_hier_qrels(hier_qrels, art_dict)
    print("Total {} pages".format(len(art_dict.keys())))
    c = 1
    with open(output_file, 'w') as out:
        for page in hier_dict.keys():
            paralist = art_dict[page]
            pos = []
            neg = []
            if len(paralist) > 1:
                for i in range(len(paralist) - 1):
                    for j in range(i + 1, len(paralist)):
                        p1 = paralist[i]
                        p2 = paralist[j]
                        if hier_dict[page][p1] == hier_dict[page][p2]:
                            pos.append(str(i)+"_"+str(j))
                        elif top_dict[page][p1] != top_dict[page][p2]:
                            neg.append(str(i)+"_"+str(j))
            out.write(page+'\n')
            out.write(" ".join(paralist)+'\n')
            out.write("Pos: "+" ".join(pos)+'\n')
            out.write("Neg: " + " ".join(neg) + '\n\n')
            c += 1
            if c%1000 == 0:
                print(str(c)+" pages processed")

def main():
    parser = argparse.ArgumentParser(description="Generate parapair dataset for parapair similarity training")
    parser.add_argument("-a", "--art_qrels", help="Path to article qrels")
    parser.add_argument("-t", "--top_qrels", help="Path to top qrels")
    parser.add_argument("-q", "--hier_qrels", help="Path to hierarchical qrels")
    parser.add_argument("-o", "--output", help="Path to output file")
    args = vars(parser.parse_args())
    art_qrels_file = args["art_qrels"]
    top_qrels_file = args["top_qrels"]
    hier_qrels_file = args["hier_qrels"]
    outfile = args["output"]
    generate_parapair(art_qrels_file, top_qrels_file, hier_qrels_file, outfile)

if __name__ == '__main__':
    main()