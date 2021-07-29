import csv
import itertools
import sys
import numpy as np

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # print("probabilities: ", probabilities)  # print print print print print print print print print

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    # print("data: \n", data)  # print print print print print print
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    '''
    print("powerset: \n",
    [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ])
    '''
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    '''
    print("\njoint_probability:\n",
          "\npeople: ", people,
          "\none_gene: ", one_gene,
          "\ntwo_genes: ", two_genes,
          "\nhave_trait: ", have_trait,
          )
    '''  # print print print print print print print print print print

    result = []  # array with probabilities (from every person) to multiply at the end
    for person in people:
        # if person has no parents in date ------------------------------------------
        if (people[person])['mother'] is None or (people[person])['father'] is None:

            if person in one_gene:
                if person in have_trait:
                    result.append(PROBS["gene"][1] * PROBS["trait"][1][True])
                else:
                    result.append(PROBS["gene"][1] * PROBS["trait"][1][False])
            elif person in two_genes:
                if person in have_trait:
                    result.append(PROBS["gene"][2] * PROBS["trait"][2][True])
                else:
                    result.append(PROBS["gene"][2] * PROBS["trait"][2][False])
            else:
                if person in have_trait:
                    result.append(PROBS["gene"][0] * PROBS["trait"][0][True])
                else:
                    result.append(PROBS["gene"][0] * PROBS["trait"][0][False])
        else:  # if person have parents in date ----------------------------------------------------------
            no_parent_person = 0  # --------------------------CHILD---------------------------------

            # prob that 2 genes so mother and father should give one genes each
            if person in two_genes:  # -----CHILD IN 2 GENES-----------
                # mother_name = person['mother']
                if people[person]['mother'] in one_gene:  # mather has 1 gens
                    probs_mother = 1/2  # - PROBS["mutation"] + PROBS["mutation"]
                elif people[person]['mother'] in two_genes:  # mather has 2 gens
                    probs_mother = 1 - PROBS["mutation"]  # prob that mather gave one gene is 100% - mutation
                else:  # mother don't have gene
                    probs_mother = PROBS["mutation"]  # only mutation can gave gene
                # the same for father
                if people[person]['father'] in one_gene:
                    probs_father = 1/2  # - PROBS["mutation"] + PROBS["mutation"]
                elif people[person]['father'] in two_genes:
                    probs_father = 1 - PROBS["mutation"]
                else:
                    probs_father = PROBS["mutation"]
                no_parent_person = probs_father * probs_mother

            elif person in one_gene:  # -----------CHILD IN ONE GENE---------------
                # scenario where mother give one gene and father 0 -> probs_mother_one , probs_father_none
                # scenario where father give one gene and mother 0 -> probs_mother_none, probs_father_one

                if people[person]['mother'] in one_gene:  # if mother have 1 gene
                    probs_mother_one = 1/2  # WHY???
                    # - PROBS["mutation"]  because 1 gen (+) can mutate to (-)
                    # + PROBS["mutation"] because 1 gen (-) can mutate to (+)
                    probs_mother_none = 1/2  # - PROBS["mutation"] + PROBS["mutation"]  # prob that she not gave gen
                elif people[person]['mother'] in two_genes:  # mother have 2 genes
                    probs_mother_one = 1 - PROBS["mutation"]  # prob that she gave 1 genes from 2
                    probs_mother_none = PROBS["mutation"]  # prob that she don't gave gen is only mutation
                else:  # if mather have 0 genes
                    probs_mother_one = PROBS["mutation"]  # prob that she gave 1 gen is only mutation
                    probs_mother_none = 1 - PROBS["mutation"]  # prob that she don't gave gene is 100%-mutation
                if people[person]['father'] in one_gene:
                    probs_father_none = 1/2  # - PROBS["mutation"] + PROBS["mutation"]
                    probs_father_one = 1/2  # - PROBS["mutation"] + PROBS["mutation"]
                elif people[person]['father'] in two_genes:
                    probs_father_none = PROBS["mutation"]
                    probs_father_one = 1 - PROBS["mutation"]
                else:
                    probs_father_none = 1 - PROBS["mutation"]
                    probs_father_one = PROBS["mutation"]

                no_parent_person = probs_mother_one * probs_father_none + probs_father_one * probs_mother_none

            else:  # ------------------CHILD IN O GENE--------------
                if people[person]['mother'] in one_gene:
                    probs_mother = 1/2  # - PROBS["mutation"] + PROBS["mutation"]
                elif people[person]['mother'] in two_genes:
                    probs_mother = PROBS["mutation"]
                else:
                    probs_mother = 1 - PROBS["mutation"]
                if people[person]['father'] in one_gene:
                    probs_father = 1 / 2  # - PROBS["mutation"] + PROBS["mutation"]
                elif people[person]['father'] in two_genes:
                    probs_father = PROBS["mutation"]
                else:
                    probs_father = 1 - PROBS["mutation"]
                no_parent_person = probs_father * probs_mother
            # CHILD have trait or not ----------------------------------
            if person in have_trait:
                if person in one_gene:
                    no_parent_person *= PROBS["trait"][1][True]
                elif person in two_genes:
                    no_parent_person *= PROBS["trait"][2][True]
                else:
                    no_parent_person *= PROBS["trait"][0][True]
            else:
                if person in one_gene:
                    no_parent_person *= PROBS["trait"][1][False]
                elif person in two_genes:
                    no_parent_person *= PROBS["trait"][2][False]
                else:
                    no_parent_person *= PROBS["trait"][0][False]
            result.append(no_parent_person)

    # print("result: ", np.prod(result))
    return np.prod(result)

    # raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    '''
    print("-------------------------------------")
    print("probabilities: ", probabilities)
    print("one gene: ", one_gene)
    print("two genes: ", two_genes)
    print("have trait: ", have_trait)
    print("p ", p)
    '''

    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p

    # raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    '''
    print("###################################")
    print("normalize before: ")
    for person in probabilities:
        print(person," : ", probabilities[person])
    '''

    for person in probabilities:
        gene = []  # blank array to keep value of gene for person
        trait = []  # blank array to keep value of trial
        # gene
        for i in probabilities[person]['gene']:
            gene.insert(0, probabilities[person]['gene'][i])  # insert because to front gene=[gene0,gene1,gene2]

        for i in probabilities[person]['gene']:
            probabilities[person]['gene'][i] = gene[i]/sum(gene)  # prob[person]['gene']['2']=gene[2]->gene2
        # trait
        for i in probabilities[person]['trait']:
            trait.insert(0, probabilities[person]['trait'][i])
        for i in probabilities[person]['trait']:
            probabilities[person]['trait'][i] = trait[i]/sum(trait)

    '''
    print("normalize after: ")
    for person in probabilities:
        print(person, " : ", probabilities[person])
    raise NotImplementedError
    '''
    

if __name__ == "__main__":
    main()
