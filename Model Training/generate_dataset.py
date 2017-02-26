from get_probs import get_all_probs_without_category_NA
from word_count import train_test_split, get_wordcount_by_category, get_word_perc
import operator
import pickle

import sys

sys.path.append('Utilities/')
from constants import categories, performance_metric_keys, ClassifierType, allClassifierTypes, problemOrCategoryKeys, \
    PlatformType


def get_num_of_top_words_as_feature(dataFilesNameHash):
    try:
        with open(dataFilesNameHash+'_num_of_top_words_as_feature.pickle') as f:
            num_of_top_words_as_feature = pickle.load(f)
            # print "\n\n\n\n num_of_top_words_as_feature = " + str(num_of_top_words_as_feature) + "\n\n\n\n"
    except:
        with open(dataFilesNameHash+'_num_of_top_words_as_feature.pickle') as f:
            num_of_top_words_as_feature = 10
            pickle.dump(num_of_top_words_as_feature, f)
            # print "\n\n\n\n exception in num of top words as feature, using default size of 10\n\n\n\n"

    return num_of_top_words_as_feature


def make_csv_files(category, sorted_perc, word_count, percentages, dataFilesNameHash):
    num_of_top_words_as_feature = get_num_of_top_words_as_feature()

    with open('data/' + category + '/' + '20feature_word_all_data_' + dataFilesNameHash + '.csv', 'w') as f:
        for w in sorted_perc[:num_of_top_words_as_feature]:
            # print w[0] + " " + str(word_count[w[0]]['yes']) + " " + str(word_count[w[0]]['no']) + " " + str(
            #     word_count[w[0]]['total'])
            f.write(w[0] + "," + str(word_count[w[0]]['yes']) + "," + str(word_count[w[0]]['no']) + "," + str(
                word_count[w[0]]['total']))
            f.write('\n')

        # print "---------------------------------------------------------"
        for w in sorted_perc[-num_of_top_words_as_feature:]:
            # print w[0] + " " + str(word_count[w[0]]['yes']) + " " + str(word_count[w[0]]['no']) + " " + str(
            #     word_count[w[0]]['total'])
            f.write(w[0] + "," + str(word_count[w[0]]['yes']) + "," + str(word_count[w[0]]['no']) + "," + str(
                word_count[w[0]]['total']))
            f.write('\n')

    with open('data/' + category + '/' + '20feature_word_all_data_' + dataFilesNameHash + '.csv', 'w') as f:
        for w in sorted_perc[:num_of_top_words_as_feature]:
            # word name
            f.write(w[0] + ",")
        f.write('\n')

        for w in sorted_perc[:num_of_top_words_as_feature]:
            # word perc
            f.write(str(w[1]) + ",")
        f.write('\n')

        for w in sorted_perc[-num_of_top_words_as_feature:]:
            # word name
            f.write(w[0] + ",")
        f.write('\n')

        for w in sorted_perc[-num_of_top_words_as_feature:]:
            # word perc
            f.write(str(w[1]) + ",")
        f.write('\n')

    with open('data/' + category + '/' + 'word_table_' + dataFilesNameHash + '.csv', 'w') as f:
        for w in word_count:
            f.write(w + "," + str(word_count[w]['yes']) + "," + str(word_count[w]['no']) + "," + str(
                word_count[w]['total']) + "," + str(percentages[w]))
            f.write('\n')


def write_dataset(category, sorted_perc, data, dataFilesNameHash):
    num_of_top_words_as_feature = get_num_of_top_words_as_feature()

    with open('data/' + category + '/' + dataFilesNameHash + '_dataset.csv', 'w') as f:
        f.write(','.join([x[0] for x in sorted_perc[:num_of_top_words_as_feature]]))
        # print ','.join([x[0] for x in sorted_perc[:num_of_top_words_as_feature]])

        f.write(',')

        f.write(','.join([x[0] for x in sorted_perc[-num_of_top_words_as_feature:]]))
        # print ','.join([x[0] for x in sorted_perc[-num_of_top_words_as_feature:]])

        f.write(',sub_size,time_limit')
        f.write(',class')
        f.write('\n')

        for t in data:
            f.write(','.join([str(x) for x in t]))
            f.write('\n')


# data can be train set or test set
def prepare_dataset(sorted_perc, data, category, platform):
    count = 0
    prepared_data = []
    num_of_top_words_as_feature = get_num_of_top_words_as_feature()

    for p in data:
        prepared_data.append([])
        features = []

        for presentWord in sorted_perc[:num_of_top_words_as_feature]:
            presentWord = presentWord[0]  # it contains tuple of word and percentage, hence [0] element for word

            if presentWord in p.modified_description.split():
                features.append(1)
            else:
                features.append(0)

        for notPresentWord in sorted_perc[-num_of_top_words_as_feature:]:
            notPresentWord = notPresentWord[0]

            if notPresentWord in p.modified_description.split():
                features.append(1)
            else:
                features.append(0)

        features.append(p.sub_size.split()[0])
        features.append(p.time_limit[:1])

        if category in p.category:
            features.append(1)
        else:
            features.append(0)

        prepared_data[count] = features
        count += 1

    return prepared_data


def generate(useIntegrated, category, platform):
    probs = get_all_probs_without_category_NA(useIntegrated, platform)

    test_size = 0.5  # default value
    # with open('test_size.pickle') as f:
    #     test_size = pickle.load(f)

    train_set, test_set = train_test_split(probs, test_size)
    word_cnt_by_cateogry = get_wordcount_by_category(train_set, category)

    percentages, word_cnt_stats = get_word_perc(word_cnt_by_cateogry)

    sorted_perc = sorted(percentages.items(), key=operator.itemgetter(1))
    sorted_perc.reverse()  # desc order

    total_data = []
    prepared_train_data = prepare_dataset(sorted_perc, train_set, category, platform)
    prepared_test_data = prepare_dataset(sorted_perc, test_set, category, platform)

    [total_data.append(t) for t in prepared_train_data]
    [total_data.append(t) for t in prepared_test_data]

    make_csv_files(category, sorted_perc, word_cnt_stats, percentages, platform)
    write_dataset(category, sorted_perc, total_data, platform)


def generateLazyLoad(useIntegrated, category, platform, dataFilesNameHash, shouldShuffle=True):
    probs = []
    if len(generateLazyLoad.probs) == 0:
        generateLazyLoad.probs = get_all_probs_without_category_NA(useIntegrated, platform)
    probs = generateLazyLoad.probs
    test_size = 0.5  # default value
    # with open('test_size.pickle') as f:
    #     test_size = pickle.load(f)

    train_set, test_set = train_test_split(probs, test_size)
    word_cnt_by_cateogry = get_wordcount_by_category(train_set, category)

    percentages, word_cnt_stats = get_word_perc(word_cnt_by_cateogry)

    sorted_perc = sorted(percentages.items(), key=operator.itemgetter(1))
    sorted_perc.reverse()  # desc order

    total_data = []
    prepared_train_data = prepare_dataset(sorted_perc, train_set, category, platform)
    prepared_test_data = prepare_dataset(sorted_perc, test_set, category, platform)

    [total_data.append(t) for t in prepared_train_data]
    [total_data.append(t) for t in prepared_test_data]

    make_csv_files(category, sorted_perc, word_cnt_stats, percentages, dataFilesNameHash)
    write_dataset(category, sorted_perc, total_data, dataFilesNameHash)


generateLazyLoad.probs = []

if __name__ == '__main__':
    generate('graph')