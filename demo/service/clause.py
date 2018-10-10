# -*- coding: utf-8 -*-
import spacy


class ClauseArticle():

    def sents_content(self, content):

        content_list = []
        summary_list = []
        article_content = self.seger.segment(content)
        for sentence in article_content:
            sentence = sentence + '。'
            content_list.append(sentence)
        if len(''.join(content_list)) <= self.max_words:
            return ('\n\n'.join(content_list),
                    ''.join(content_list))
        else:
            for sentences in content_list:
                summary_list.append(sentences)
                if len(''.join(summary_list)) > self.max_words:
                    return ('\n\n'.join(content_list),
                            ''.join(summary_list))

    def sents(self, text):

        nlp = spacy.load('en_core_web_sm')
        text = text.replace('\r', '').replace('\n', '')
        text = text.replace('"', '“').replace('"', '”')
        doc = nlp(text)
        return '\n\n'.join(map(str, list(doc.sents)))
