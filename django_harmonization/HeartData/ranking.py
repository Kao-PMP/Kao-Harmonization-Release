#!/usr/bin/env python3
'''
   Copyright 2017 The Regents of the University of Colorado

   Licensed under the Apache License, Version 2.0 (the "License")
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
'''
 ranking.py <db name> <userid> <study id> <extraction id>
    - study id from the study table, indicating the input study
    - extraction id referring to a set of rows in categorization_function_metadata sharing the as-yet to be renamed study_id

 Python Version: 3.6.3

 finds the tertile numbers based on position in the sorted array
 Use as a sanity check. The actual values used will be ones derived from clinical experience.

 It uses the number of parameters in the categorization rules of the given extraction_id as
 the number of buckets/bins for each attribute/phenotype. 
 TODO make this configurable so  you can get tertiles or quartiles.

 This is research code for demonstration purposes only.

 croeder 10/2017 chris.roeder@ucdenver.edu
'''

import collections
import logging
import sys

from categorization import CategorizationRule
from person import BasePerson

import observation
import psycopg2
import psycopg2.extras
import argh


def get_extraction_matrix_bins(con, person_ids, extraction_id):
    """ finds max values for a set of n bins.
        returns a map from an extracted attribute name (long_name), to a map of bins.
        Those maps are from the tertile (1..n), to the maximum value of that bin.
        long_name -> bin_number -> max_value
    """
    bins_by_attribute = collections.defaultdict(list)
    failing_rules =  set()
    categorization_rules = CategorizationRule.load_rules(con, extraction_id)
    for rule_attribute in categorization_rules.keys():
        rules = categorization_rules[rule_attribute]
        logger.info("CatRule attribute %s rule count %s", rule_attribute, len(rules))
        for rule in rules: # assumes only a single will qualify
            # (not dealing with qualification here, just check them regardless.
            # If an attribute has 2 rules, run them both)
            if rule._function_name != 'map_concept_id':
                # TODO that thing about deducing the type by the function again
                # logger.info("CatRule attribute %s rule %s", rule_attribute, rule)
                num_bins = rule.get_num_bins()

                values = []
                for person_id in person_ids:
                    ohdsi_tuples = observation.fetch(con, rule._from_table, person_id,
                                                            rule._from_vocabulary_id,
                                                            rule._from_concept_code)
                    if ohdsi_tuples != None and len(ohdsi_tuples) > 0:
                        # TODO get first non-null value, not the first blindly:
                        (number, _, _, _) = ohdsi_tuples[0]
                        if number is not None:
                            values.append(number)
                        else:
                            logger.error(" none value? {} {}", ohdsi_tuples, rule)
                    else:
                        failing_rules.add(rule)

                if values:
                    values.sort()
                    if num_bins > 0:
                        bin_size = len(values)/num_bins
                        for value_bin in range(1, num_bins+1):
                            bin_index = int(round(value_bin * bin_size -1))
                            try:
                                bins_by_attribute[rule_attribute].append(
                                    values[bin_index])
                                logger.info("BINS: a:%s bin:%s index:%s num:%s, size:%s, value:%s",
                                            rule_attribute, value_bin, bin_index, num_bins, round(bin_size,3), values[bin_index])
                            except Exception as exception:
                                logger.error(exception)
                                logger.error("bogus bin_index: %s   %s %s", bin_index, value_bin, bin_size)
                                logger.error("_get_extraction_matrix_bins e:%s len:%s  used:%s",
                                             exception, len(values), value_bin * bin_size -1)
                                logger.error(("_get_extraction_matrix_bins att:%s bin:%s, "
                                              "bin_size:%s, num_bins:%s"),
                                             rule_attribute, value_bin, bin_size, num_bins)
                    else:
                        logger.warning("0 num_bins  %s", rule)
                else:
                    logger.warning("_get_extraction_matrix_bins() no values for %s", rule)

    for rule in failing_rules:
        logger.info("FAILing rule: %s", rule)
    return bins_by_attribute


def main(db_name, user_name, study_name, extraction_id) :


    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

    conn = psycopg2.connect(database=db_name, user=user_name)

    # limited persons on one study
    person_obj = BasePerson.factory(study_id)
    person_ids = person_obj.get_study_person_ids(conn)

    logger.info("extracting %d", len(person_ids))

    bins_map = get_extraction_matrix_bins(conn, person_ids, extraction_id)
    print("===================")
    for attribute in bins_map.keys():
        for bin_number in range(0, len(bins_map[attribute])):
            print(attribute.replace(" ", ""), bin_number, bins_map[attribute][bin_number])

    conn.close()


if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
    
