import argparse
import json
import os
import re
import sys
from copy import copy
from importlib import import_module

from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env", verbose=True)
print(os.getenv("CHURN_DB_USER"))
print(os.getenv("CHURN_DB"))
import pandas as pd
from postgres import Postgres

"""
####################################################################################################
Arguments
"""
parser = argparse.ArgumentParser()
# Run control arguments
parser.add_argument(
    "--schema", type=str, help="The name of the schema", default="churn_studies"
)
parser.add_argument("--chapter", type=int, help="The chapter of the listing", default=3)
parser.add_argument(
    "--listing", nargs="*", type=int, help="The number of the listing", default=[11]
)
parser.add_argument(
    "--insert",
    action="store_true",
    default=False,
    help="Use the insert version of a metric SQL, if available",
)
parser.add_argument(
    "--version",
    nargs="*",
    help="Alternative listing _parameter_ verions (optional)",
    default=[],
)


"""
####################################################################################################
Constants
"""

pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
print_num_rows = 10

reserved_param_keywords = (
    "listing",
    "mode",
    "type",
    "schema",
    "name",
    "chapter",
    "full_name",
)

"""
####################################################################################################
Functions
"""


def _full_listing_name(chapter, listing, name, insert=False):
    """
    Creates the name of a listing file from the components.
    The names are like "listing_C_N_<name>" where C is the chapter, N is the number and
    <name> is the listing name.  For example, "listing_2_1_net_retention".
    "insert" listings are a special SQL listing type used in chapter 7.
    :param chapter:
    :param listing:
    :param name:
    :param insert:
    :return:
    """
    prefix = "listing" if not insert else "insert"
    full_name = f"{prefix}_{chapter}_{listing}_{name}"
    return full_name


def _sql_listing_from_params(param_dict, insert):
    """
    Utility to take parameters in a dictionary loaded from configuration, and call the sql_listing function
    Pops those dictionary parameters that are parameters of the sql_listing parameters, and passes what is
    left as the bind variables
    :param param_dict:
    :param insert:
    :return:
    """
    chapter = param_dict.pop("chapter")
    listing = param_dict.pop("listing")
    name = param_dict.pop("name")
    schema = param_dict.pop("schema")
    mode = param_dict.pop("mode")
    save_ext = param_dict.pop("save_ext") if "save_ext" in param_dict else None
    sql_listing(
        chapter,
        listing,
        name,
        schema,
        mode,
        param_dict,
        insert=insert,
        save_ext=save_ext,
    )


def sql_listing(
    chapter, listing, name, schema, mode, param_dict, insert=False, save_ext=None
):
    """

    Run a SQL listing.  The sql file is loaded, and then any non-reserved keyword in the parameters is treated as a
    string to be replaced in the sql string. The SQL is then printed out.

    :param chapter:
    :param listing:
    :param name:
    :param schema:
    :param mode:The allowed modes are:
        run : The SQL returns no result
        one : The SQL should return one row result to be printed
        top : The SQL returns many results, print the top N (given by global print_num_rows)
    :param param_dict: the bind variables as a dictionary
    :param insert: flag to use the insert form of a query; see chapter 7
    :param save_ext:
    :return:
    """

    with open(
        "../../listings/chap%d/%s.sql"
        % (chapter, _full_listing_name(chapter, listing, name, insert)),
        "r",
    ) as myfile:

        db = Postgres(
            "postgres://%s:%s@localhost/%s"
            % (
                os.environ["CHURN_DB_USER"],
                os.environ["CHURN_DB_PASS"],
                os.environ["CHURN_DB"],
            )
        )

        # prefix the search path onto the listing, which does not specify the schema
        sql = "set search_path = '%s'; " % schema

        # load the sql file
        sql = sql + myfile.read()

        # bind any parameters that match strings in the sql
        param_keys = [p for p in param_dict.keys() if p not in reserved_param_keywords]
        for p in param_keys:
            sql = sql.replace(p, str(param_dict[p]))

        # Print the sql (then remove the newlines)
        print("SQL:\n----------\n" + sql + "\n----------\nRESULT:")
        sql = sql.replace("\n", " ")

        # Run in the manner indicated by the mode
        if mode == "run":
            db.run(sql)
        elif mode == "one":
            res = db.one(sql)
            print(res)
        elif mode == "top" or mode == "save":
            res = db.all(sql)
            df = pd.DataFrame(res)
            if mode == "save":
                save_path = "../../../fight-churn-output/" + schema + "/"
                os.makedirs(save_path, exist_ok=True)
                csv_path = (
                    save_path
                    + schema
                    + "_"
                    + name.replace("listing_{}_{}_".format(chapter, listing), "")
                )
                if save_ext:
                    csv_path = csv_path + "_" + save_ext
                csv_path = csv_path + ".csv"
                print("Saving: %s" % csv_path)
                df.to_csv(csv_path, index=False)
            else:
                print(df.head(print_num_rows))
        else:
            print("Unknown run mode for SQL example")
            exit(-4)


def _python_listing_from_params(param_dict):
    """
    Utility to call the python_listing function from a parameter dictionary, loaded from the configuration
    Pops the parameters that are part of the function signature, and passes the remaining parameters as dictionary
    of function parameters
    :param param_dict:
    :return:
    """
    chapter = param_dict.pop("chapter")
    listing = param_dict.pop("listing")
    name = param_dict.pop("name")

    python_listing(chapter, listing, name, param_dict)


def python_listing(chapter, listing, name, param_dict):
    """
    Runs one python code listing.  Each listing is defined as a model, and should have one function in it, which is the name of
    the listing file, without the part saying listing_X_Y.  If the function is found in the module it is run; all of the
    non-reserved keywords in the parameter dictionary are treated as the parameters
    :param chapter:
    :param listing:
    :param name:
    :param param_dict: dictionary produced by load_and_check_listing_params
    :return:
    """

    # make a dictionary of just the non-reserved keywords, which should be the parameters
    example_params = {}
    for k in param_dict.keys():
        if k in reserved_param_keywords:
            continue
        example_params[k] = param_dict[k]

    # Load the listing name module
    full_name = _full_listing_name(chapter, listing, name)
    mod = import_module(full_name)

    ex_fun = getattr(mod, name, None)
    if ex_fun is not None:
        # Run the function, passing the parameters
        ex_fun(**example_params)
    else:
        print("Could not find function %s in module %s" % (name, full_name))
        exit(-5)


def load_and_check_listing_params(args):
    """
    Loads the JSON of parameters for this schema, and gets the parameters for the specified listing. It raises errors if
    it cannot find what it is looking for. Once it finds the entry for this listing, it starts with the chapter default
    params, and then adds any parameters specific to the listing (which would override the chapter parameters, if there
    was one of the same name.) It also adds context information to the result, so that it has all the information needed
    when the listings are run.

    :param args: result of parsing arguments
    :return: dictionary of name value pairs for the example
    """
    schema = args.schema
    chapter = args.chapter
    listing = args.listing
    version = args.version

    chapter_key = f"chap{chapter}"
    list_key = f"list{listing}"
    vers_key = f"v{version}" if version else None

    # Error if there is no file for this schema
    conf_path = "../../listings/conf/%s_listings.json" % schema
    if not os.path.isfile(conf_path):
        print(f"No params {conf_path} to run listings on schema {schema}")
        exit(-1)

    with open(conf_path, "r") as myfile:
        param_dict = json.loads(myfile.read())

    # Error if there is no key for this chapter in the dictionary
    if chapter_key not in param_dict:
        print(f"No params for chapter {chapter} in {schema}_listings.json")
        exit(-2)

    # Error if there is no key for this listing
    if list_key not in param_dict[chapter_key]:
        print(f"No listing for chapter {chapter} in {schema}_listings.json")
        exit(-3)

    # Start with the chapter default parameters
    listing_params = copy(param_dict[chapter_key]["defaults"])

    # If using the insert option, set the parameter source to insert sub-block rather than regular
    if args.insert:
        if "insert" not in param_dict[chapter_key][list_key]:
            print(f"No insert section for chapter {chapter} in {schema}_listings.json")
            exit(-4)
        param_source = param_dict[chapter_key][list_key]["insert"]
        # force the right mode forn insert sqls
        listing_params["mode"] = "run"
    else:
        param_source = param_dict[chapter_key][list_key]

    # Add additional specific parameters for this listing, possibly overwriting defaults
    if len(param_source["params"]) > 0:
        for k in param_source["params"].keys():
            listing_params[k] = param_source["params"][k]

    # add additional specific parmeters for this version (if any), possibly overwriting
    if vers_key and vers_key in param_source:
        for k in param_source[vers_key].keys():
            listing_params[k] = param_source[vers_key][k]

    # Add the contextual information
    listing_params["schema"] = schema
    listing_params["chapter"] = chapter
    listing_params["listing"] = listing
    listing_params["name"] = param_dict[chapter_key][list_key]["name"]

    return listing_params

    # Another error if it didn't find a listing


def run_one_listing(args):
    """
    Load the dictionary of parameters for this schema
    Check the type of the listing (SQL or Python) and call the executor function
    :param args: from arg parse
    :return:
    """
    # Get arguments
    listing_params = load_and_check_listing_params(args)

    print(
        "\nRunning chapter %d listing %d %s on schema %s"
        % (args.chapter, args.listing, listing_params["name"], args.schema)
    )

    # Run the executor function for sql or for python...
    type = listing_params.get(
        "type", listing_params["type"]
    )  # chap params should always have type
    if type == "sql":
        _sql_listing_from_params(listing_params, args.insert)
    elif type == "py":
        _python_listing_from_params(listing_params)
    else:
        raise Exception("Unsupported type %s" % type)


"""
####################################################################################################
The main script for running Fight Churn With Data examples.
This will loop over multiple listings and versions in one chapter.
"""

if __name__ == "__main__":
    args, _ = parser.parse_known_args()

    for l in args.listing:
        list_args = copy(args)
        list_args.listing = l
        if len(args.version) == 0:
            list_args.version = None
            run_one_listing(list_args)
        else:
            for v in args.version:
                vers_args = copy(list_args)
                vers_args.version = v
                run_one_listing(vers_args)
