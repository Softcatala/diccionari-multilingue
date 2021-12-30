import xml.etree.ElementTree as ET
import json

# http://wordnetweb.princeton.edu/
# http://compling.hss.ntu.edu.sg/omw/cgi-bin/wn-gridx.cgi?usrname=&gridmode=grid

def load_catalan():
    synset_ids = {}

    with open('catalan/mcr/wn-data-cat.tab') as f:        
        lines = [line.rstrip() for line in f]

    for line in lines:
        if line[0] == '#':
            continue

        components = line.split('\t')

        synset_id = components[0].strip()
        word = components[2].strip()
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

    print(f"Loaded catalan terms {len(synset_ids)}")
    return synset_ids

def show_item(id, terms):
    print("---")
    print(f"id: {id}")
    for term in terms:
        print(f"term: {term}")

def main():

    catalan_def = 0
    english_def = 0


    synset_ids_catalan = load_catalan()
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
                #print(f"{item} - {synset.attrib[item]}")
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
#                    print(attrib)
                    if attrib == 'desc':
                        if item.attrib[attrib] == 'text':
                            for text_tag in item.iter('text'):
                                en_label = text_tag.text
            
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
            terms.append(term)

    with open('terms.json', 'w') as outfile:
        json.dump(terms, outfile, indent=4, ensure_ascii=False)
        
    print(f"English {english_def}, catalan {catalan_def}, written {len(terms)}")
if __name__ == "__main__":
    main()
