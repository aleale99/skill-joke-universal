from os.path import join, dirname, exists
from os import listdir, makedirs
from mtranslate import translate
import unicodedata
import re
from time import sleep


def fix_tx(tx):
    # fix encoding
    tx = unicodedata.normalize('NFKD', tx).encode('ascii', 'ignore')
    # fix removal of "{" and "}" during translate process
    words = tx.split(" ")
    to_add = []
    for i, word in enumerate(words):
        prev = words[i-1] if i > 0 else ""
        #prev_prev = words[i - 2] if i > 1 else ""
        nxt = words[i + 1] if i + 1 < len(words) else ""
        #nxt_nxt = words[i + 2] if i + 2 < len(words) else ""
        if nxt == "}" and prev != "{":
            # removed in tx
            to_add.append((i, "{"))
        if prev == "{" and nxt != "}":
            # removed in tx
            to_add.append((i+1, "}"))
        if nxt == "}}" and prev != "{{":
            # removed in tx
            to_add.append((i, "{{"))
        if prev == "{{" and nxt != "}}":
            # removed in tx
            to_add.append((i+1, "}}"))
    for i, c in to_add:
        words.insert(i, c)
    return " ".join(words).replace("{ ", "{").replace(" }", "}")


# tx intents
def tx_intents(lang):
    intents_path = join(dirname(__file__), "vocab", source_lang)
    target_path = join(dirname(__file__), "vocab", lang)
    if not exists(intents_path):
        return
    if not exists(target_path):
        makedirs(target_path)
    files = listdir(intents_path)
    existing_files = listdir(target_path)
    for file in files:
        if file in existing_files:
            continue
        if ".intent" in file or ".entity" in file:
            print "translating", file, "from", source_lang, "to", lang
            with open(join(intents_path, file), "r") as f:
                source_lines = f.readlines()
            with open(join(target_path, file), "w") as f:
                total = []
                for line in source_lines:
                    try:
                        print "line", line
                        original_tags = [l.replace(" ","") for l in
                                          re.findall('\{[^}]*\}', line)]
                        tx = translate(line, lang, source_lang)

                        sleep(1) # dont spam api
                        tx = fix_tx(tx)

                        translated_tags = [l.replace(" ","") for l in
                                            re.findall('\{[^}]*\}', tx)]

                        for i in xrange(0, len(translated_tags)):
                            tx = tx.replace(translated_tags[i], original_tags[i])
                        tx += "\n"
                        if tx not in total: # check duplicates, happens in tx
                            f.write(tx)
                            total.append(tx)
                            print "translated", tx
                    except Exception as e:
                        print e


# tx dialogs
def tx_dialogs(lang):
    dialog_path = join(dirname(__file__), "dialog", source_lang)
    target_path = join(dirname(__file__), "dialog", lang)
    if not exists(dialog_path):
        return
    if not exists(target_path):
        makedirs(target_path)
    files = listdir(dialog_path)
    existing_files = listdir(target_path)
    for file in files:
        if file in existing_files:
            continue
        if ".dialog" in file:
            print "translating", file, "from", source_lang, "to", lang
            with open(join(dialog_path, file), "r") as f:
                source_lines = f.readlines()
            with open(join(target_path, file), "w") as f:
                total = []
                for line in source_lines:
                    print "line", line
                    original_tags = [l.replace(" ","") for l in
                                        re.findall('\{\{[^}]*\}\}', line)]
                    tx = translate(line, lang, source_lang)
                    sleep(1)  # dont spam api
                    tx = fix_tx(tx)
                    translated_tags = [l.replace(" ","") for l in
                                        re.findall('\{\{[^}]*\}\}', tx)]
                    for i in xrange(0, len(translated_tags)):
                        tx = tx.replace(translated_tags[i], original_tags[i])
                    if tx not in total:
                        f.write(tx+"\n")
                        total.append(tx)
                        print "translated", tx


if __name__ == "__main__":
    source_lang = "en-us"
    target_langs = ["es-es", "fr-fr", "de-de", "it-it", "pt-pt", "pt-br"]

    # because of low accuracy this does not attempt .voc files
    # or .rx files
    for lang in target_langs:
        tx_intents(lang)
        tx_dialogs(lang)