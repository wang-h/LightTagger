import os

import datetime


def read_CoNLL_sentence_single_file(path, tag_id_mapping):
    with open(path, "r") as f:
        sentence = []
        tags = []
        while True:
            line = f.readline()
            if line == "\n":
                if len(sentence) > 0:
                    yield sentence, tags
                    sentence = []
                    tags = []
            elif line == "":
                break
            else:
                line = line.rstrip("\r\n")
                token = line.split()[0]
                sentence.append(token)
                tag = "O" if len(line.rstrip("\r\n")) < 2 else line.split()[
                    1].split("-")[-1]
                tags.append(tag_id_mapping[tag])
        if len(sentence) > 0:
            yield sentence, tags
    f.close()


class DataLoader:
    @staticmethod
    def read_CoNLL_format_files(path, tag_id_mapping):
        sentences = []
        for path, subdirs, files in os.walk(path):
            for name in files:
                for sentence, tags in read_CoNLL_sentence_single_file(os.path.join(path, name), tag_id_mapping):
                    sentences.append([tuple(sentence), tuple(tags)])
        return sentences

    @staticmethod
    def save_CoNLL_format_files(prev_path, examples, tag_id_mapping):
        data_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".txt"
        file_name = os.path.join("./",  data_info)
        id_tag_mapping = {k: v for v, k in tag_id_mapping.items()}
        with open(file_name, "w") as fout:
            for sentence in examples:
                tokens, tag_ids = sentence
                length = len(tokens)
                tags = []
                for i, (token, tid) in enumerate(zip(tokens, tag_ids)):
                    tag = id_tag_mapping[tid]
                    if i == 0:
                        if tid != 0:
                            tag = "B-" + tag
                    else:
                        pre_tid = tag_ids[i-1]
                        if pre_tid != tid:
                            if tid != 0:
                                tag = "B-" + tag
                        else:
                            if tid != 0:
                                tag = "I-" + tag
                    tags.append(tag)
                for (token, tag) in zip(tokens, tags):
                    fout.write("{} {}\n".format(token, tag))
                fout.write("\n")
        return file_name, True
