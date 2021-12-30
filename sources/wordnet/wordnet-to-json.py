 import xml.etree.ElementTree as ET
import json
import unicodedata

# http://wordnetweb.princeton.edu/
# http://compling.hss.ntu.edu.sg/omw/cgi-bin/wn-gridx.cgi?usrname=&gridmode=grid



def load_term_catalan():
    WORD = 0
    CAT_ID = 2

    synset_ids = {}

    # Format 'Brussel·les	1	cat-30-08850450-n	n	99.0	None	------'
    with open('data/3.0/ca/wei_cat-30_variant.tsv') as f:
        lines = [line.rstrip() for line in f]

    for line in lines:
        if line[0] == '#':
            continue

        components = line.split('\t')
        word = components[WORD].strip()
        cat_synset_id = components[CAT_ID].strip()
        synset_id = cat_synset_id.replace('cat-30-', '')
        
        if synset_id in synset_ids:
            ids = synset_ids[synset_id]
            ids.append(word)
            synset_ids[synset_id] = ids
        else:
            words = [word]
            synset_ids[synset_id] = words

       
    for synset_id in synset_ids.keys():
#        print(f"'{synset_id}'")
        for value in synset_ids[synset_id]:
#            print(f" {value}")
            continue

    print(f"load_term_catalan {len(synset_ids)}")
    return synset_ids


def load_label_catalan():

    DEFINITION = 6
    CAT_ID = 0
    synset_ids = {}

    # Format 'cat-30-00001740-n	n	82546	-	-	0	Realitat considerada per abstracció com a unitat (amb o sense vida)	19	0	------'
    with open('data/3.0/ca/wei_cat-30_synset.tsv') as f:
        lines = [line.rstrip() for line in f]

    for line in lines:
        if line[0] == '#':
            continue

        components = line.split('\t')
        label = components[DEFINITION].strip()

        cat_synset_id = components[CAT_ID].strip()
        synset_id = cat_synset_id.replace('cat-30-', '')
        if label == 'None' or len(label) == 0:
            continue

        synset_ids[synset_id] = label

    for synset_id in synset_ids.keys():
#        print(f"'{synset_id}'")
        for value in synset_ids[synset_id]:
#            print(f" {value}")
            continue

    print(f"load_label_catalan {len(synset_ids)}")
    return synset_ids

def load_catalan():
    terms = load_term_catalan()
    labels = load_label_catalan()
    return terms, labels

def show_item(id, terms):
    print("---")
    print(f"id: {id}")
    for term in terms:
        print(f"term: {term}")

def main():

    catalan_def = 0
    english_def = 0


    synset_ids_catalan, labels_catalan = load_catalan()
    terms = []
    for filename in ['verb.xml', 'noun.xml', 'adv.xml', 'adj.xml']:
        path = 'WordNet-3.0/glosstag/merged/'
        tree = ET.parse(path + filename)
        root = tree.getroot()

        for synset in root.iter('synset'):
            id = None
            pos = None
       
            # Read <synset> tag attributes
            for item in synset.attrib:
                if item == 'id':
                    id = synset.attrib[item]

                if item == 'pos':
                    pos = synset.attrib[item]

            # Read terms
            en_terms = []
            for item in synset.iter('term'):
                en_terms.append(item.text)

            english_def += 1

            # gloss desc="orig"
            en_terms = []
            en_label = ''
            for item in synset.iter('gloss'):
                for attrib in item.attrib:
                    if attrib == 'desc':
                        if item.attrib[attrib] == 'text':
                            for text_tag in item.iter('text'):
                                en_label = text_tag.text
                                en_label = en_label.replace('â', '')
                                en_label = en_label.replace('', '')

            
            catalan_id = f"{id[1:]}-{id[0]}"
    #        print(f"cat_id: '{catalan_id}'")
            ca_terms = []
            if catalan_id in synset_ids_catalan:
                catalan_def += 1
                for value in synset_ids_catalan[catalan_id]:
                    ca_terms.append(value)
                    #print(f"catalan: {value}")
#                    pass
            if len(ca_terms) == 0 or len(en_label) == 0:
                continue

            term = {}
            term['id'] = id
            term['pos'] = pos
            term['en'] = en_terms
            term['en_label'] = en_label
            term['ca'] = ca_terms

            if id in labels_catalan:
                term['ca_label'] = labels_catalan[id]

            terms.append(term)

    with open('terms.json', 'w') as outfile:
        json.dump(terms[:100], outfile, indent=4, ensure_ascii=False)
        
    print(f"English {english_def}, catalan {catalan_def}, written {len(terms)}")
if __name__ == "__main__":
    main()
