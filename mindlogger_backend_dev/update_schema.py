import json
import os
import pandas as pd
from urllib.parse import quote
import sys
from urllib.request import urlopen
__package__ = "mindlogger_backend_dev.update_schema"
from ..object_manipulation import *


def add_to_schedule(
    girder_connection,
    frequency,
    schedules_id,
    activity_item_id,
    context={},
    timings={
        "1d": "Daily",
        "1": "Once",
        "8h": "3×Daily",
        "12h": "2×Daily"
    },
    schedule_folder_id=None,
    schedule_item_id=None
):
    """
    Function to add Activities to a Schedule

    Parameters
    ----------
    girder_connection: GirderClient

    frequency: string

    schedules_id: string

    activity_item_id: string

    context: dictionary, optional
        default: {}

    timings: dictionary, optional
        key: string
            frequency
        value: string
            schedule name
        default: {
            "1d": "Daily",
            "1": "Once",
            "8h": "3×Daily",
            "12h": "2×Daily"
        }

    schedule_folder_id: string, optional
        default: _id for public schedules

    schedule_item_id: string, optional
        default: _id for "Version 0 [Frequency]"

    Returns
    -------
    schedule_item_id: string

    Examples
    --------
    >>> from .. import girder_connections
    >>> import os
    >>> config_file = os.path.join(
    ...    os.path.dirname(__file__),
    ...    "config.json.template"
    ... )
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=config_file
    ... )
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config["girder-dev"]["user"],
    ...         config["girder-dev"]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> collection_id = get_girder_id_by_name(
    ...     girder_connection,
    ...     "Collection",
    ...     "Ancient One"
    ... )
    >>> schedules_id = get_girder_id_by_name(
    ...     girder_connection,
    ...     "folder",
    ...     "Schedules",
    ...     ("Collection", collection_id)
    ... )
    >>> girder_connection.get("item/{}".format(
    ...     add_to_schedule(
    ...         girder_connection=girder_connection,
    ...         frequency="Centennially",
    ...         schedules_id=schedules_id,
    ...         activity_item_id=get_girder_id_by_name(
    ...             girder_connection,
    ...             "Item",
    ...             "Fighting Dragon Raiders",
    ...             ("Folder", get_girder_id_by_name(
    ...                 girder_connection,
    ...                 "Folder",
    ...                 "Fighting Dragon Raiders",
    ...                 ("Folder", get_girder_id_by_name(
    ...                     girder_connection,
    ...                     "Folder",
    ...                     "Activities",
    ...                     ("Collection", collection_id)
    ...                 ))
    ...             ))
    ...         ),
    ...         timings={"Centennially": "Centennially"},
    ...         schedule_folder_id=schedules_id,
    ...         schedule_item_id=get_girder_id_by_name(
    ...             girder_connection,
    ...             "Item",
    ...             "Centennially",
    ...             ("Folder", schedules_id)
    ...         )
    ...     )
    ... ))['name']
    'Centennially'
    """
    schedule_folder_id = girder_connection.createFolder(
        name=timings[frequency],
        parentId=schedules_id,
        parentType="collection",
        public=False,
        reuseExisting=True
    )[
        "_id"
    ] if not schedule_folder_id else schedule_folder_id
    schedule_item_id = girder_connection.createItem(
        name=" ".join([
            "Version 0",
            timings[frequency]
        ]),
        parentFolderId=schedule_folder_id,
        reuseExisting=True
    )[
        "_id"
    ] if not schedule_item_id else schedule_item_id
    schedule_item = girder_connection.get(
        "".join([
            "item/",
            schedule_item_id
        ])
    )
    schedule_metadata = schedule_item[
        "meta"
    ] if "meta" in schedule_item else {}
    schedule_metadata[
        "@context"
    ] = context if "@context" not in \
    schedule_metadata else schedule_metadata[
        "@context"
    ]
    schedule_metadata["activities"] = [] if (
        "activities" not in schedule_metadata
    ) else schedule_metadata["activities"]
    schedule_metadata["activities"].append(
        {
            "@id": "".join([
                "item/",
                activity_item_id
            ]),
            "name": girder_connection.get(
                "item/{0}".format(
                    activity_item_id
                )
            )["name"]
        }
    )
    girder_connection.addMetadataToItem(
        schedule_item_id,
        drop_empty_keys(
            schedule_metadata
        )
    )
    return(schedule_item_id)


def camelCase(s):
    """
    Function to turn _-delimited strings to camelCase

    Parameter
    ---------
    s: string

    Returns
    -------
    cc: string

    Examples
    --------
    >>> camelCase("bob_the_builder")
    'bobTheBuilder'
    >>> camelCase(12)
    12
    """
    if not isinstance(s, str):
        return(s)
    cc = ""
    camel = False
    for c in s:
        if camel:
            cc += c.upper()
            camel=False
        elif c=="_":
            camel=True
        else:
            cc += c
    return(cc)


def camelCaseKeys(d):
    """
    Function to CamelCase each _-delimited
    key in a nested dictionary

    Parameter
    ---------
    d: dict

    Returns
    -------
    d: dict

    Examples
    --------
    >>> camelCaseKeys({
    ...     'response_type': None,
    ...     'rows': [
    ...         {'headers': [{'@value': ''}, {'@value': ''}]},
    ...         {
    ...             'index': {'@value': ''},
    ...             'options': [
    ...                 {'question_image': None, 'question_text': {'@value': ''}},
    ...                 {'question_image': None, 'question_text': {'@value': ''}}
    ...             ],
    ...             'select': {'max': 1, 'min': 1}},
    ...         {
    ...             'index': {'@value': ''},
    ...             'options': [
    ...                 {'question_image': None, 'question_text': {'@value': ''}},
    ...                 {'question_image': None, 'question_text': {'@value': ''}}
    ...             ],
    ...             'select': {'max': 1, 'min': 1}
    ...         },
    ...         {
    ...             'index': {'@value': ''},
    ...             'options': [
    ...                 {'question_image': None, 'question_text': {'@value': ''}},
    ...                 {'question_image': None, 'question_text': {'@value': ''}}
    ...             ],
    ...             'select': {'max': 1, 'min': 1}
    ...         }
    ...     ]
    ... })
    {'responseType': None, 'rows': [{'headers': [{'@value': ''}, {'@value': ''}]}, {'index': {'@value': ''}, 'options': [{'questionImage': None, 'questionText': {'@value': ''}}, {'questionImage': None, 'questionText': {'@value': ''}}], 'select': {'max': 1, 'min': 1}}, {'index': {'@value': ''}, 'options': [{'questionImage': None, 'questionText': {'@value': ''}}, {'questionImage': None, 'questionText': {'@value': ''}}], 'select': {'max': 1, 'min': 1}}, {'index': {'@value': ''}, 'options': [{'questionImage': None, 'questionText': {'@value': ''}}, {'questionImage': None, 'questionText': {'@value': ''}}], 'select': {'max': 1, 'min': 1}}]}
    >>> camelCaseKeys("test_this")
    'testThis'
    """
    if isinstance(d, str):
        return(camelCase(d))
    dd = {}
    for k in d:
        if isinstance(d[k], list):
            dd[camelCase(k)] = [
                camelCaseKeys(li) for li in d[k]
            ]
        elif isinstance(d[k], dict):
            dd[camelCase(k)] = camelCaseKeys(d[k])
        else:
            dd[camelCase(k)] = d[k]
    return(dd)


def camelCaseMeta(girderConnection, o):
    """
    Function to camelCase metadata keys on Girder

    Parameters
    ----------
    girderConnection: GirderClient

    o: dict

    Returns
    -------
    None

    Example
    -------
    >>> import json, os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> book = find_or_create(
    ...     ("Folder", "Book of Cagliostro"),
    ...     ("Collection", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Collection",
    ...         "Ancient One"
    ...     )),
    ...     girder_connection
    ... )
    >>> incantation = find_or_create(
    ...     ("Item", "draw energy from the Dark Dimension"),
    ...     ("Folder", book),
    ...     girder_connection
    ... )
    >>> inner_book = find_or_create(
    ...     ("Folder", "coloring pages"),
    ...     ("Folder", book),
    ...     girder_connection
    ... )
    >>> o = girder_connection.put(
    ...     'folder/{}'.format(book),
    ...     parameters={"metadata": json.dumps({
    ...         "test_case": ["test_one", {"test_2": "test_3"}]
    ...     })}
    ... )
    >>> from urllib.request import urlopen
    >>> image_stream = urlopen(
    ...     "/".join([
    ...         "https://vignette.wikia.nocookie.net",
    ...         "marvelcinematicuniverse/images/1/14/",
    ...         "DS_Kaecilius_Poster_cropped.png"
    ...     ])
    ... )
    >>> img_id = girder_connection.uploadFile(
    ...     parentId=incantation,
    ...     parentType="item",
    ...     stream=image_stream,
    ...     name="Kaecilius.png",
    ...     size=int(
    ...         image_stream.info()["Content-Length"]
    ...     )
    ... )["_id"]
    >>> camelCaseMeta(girder_connection, o)
    >>> girder_connection.get('folder/{}'.format(book))['meta']['testCase']
    ['testOne', {'test2': 'test_3'}]
    """
    if "meta" in o:
        girderConnection.put(
            "{}/{}".format(
                o["_modelType"],
                o["_id"]
            ),
            parameters={
                "metadata": json.dumps(
                    camelCaseKeys(o["meta"])
                )
            }
        )
    if o["_modelType"] in [
        'collection',
        'folder'
    ]:
        for folder in girderConnection.get(
            'folder?parentType={}&parentId={}'.format(
                o["_modelType"],
                o["_id"]
            )
        ):
            camelCaseMeta(
                girderConnection,
                folder
            )
    if o["_modelType"] == 'folder':
        for item in girderConnection.get(
            'item?folderId={}'.format(
                o["_id"]
            )
        ):
            camelCaseMeta(
                girderConnection,
                item
            )
    if o["_modelType"] == 'item':
        for file in girderConnection.get(
            'item/{}/files'.format(
                o["_id"]
            )
        ):
            camelCaseMeta(
                girderConnection,
                file
            )


def find_or_create(x, parent, girder_connection):
    """
    Function to find or create a Girder Folder or Item
    under a specific parent.

    Parameters
    ----------
    x: 2-tuple
        x[0]: string
            "Folder", "Item", etc.
        x[1]: string
            entity name

    parent: 2-tuple
        parent[0]: string
            "Collection", "Folder", etc.
        parent[1]: string
            Girder_id

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    _id: string
        Girder_id of found or created entity

    Examples
    --------
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> book = girder_connection.get("folder/{}".format(find_or_create(
    ...     ("Folder", "Book of Cagliostro"),
    ...     ("Collection", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Collection",
    ...         "Ancient One"
    ...     )),
    ...     girder_connection
    ... )))
    >>> book['name']
    'Book of Cagliostro'
    >>> incantation = girder_connection.get("item/{}".format(find_or_create(
    ...     ("Item", "draw energy from the Dark Dimension"),
    ...     ("Folder", book["_id"]),
    ...     girder_connection
    ... )))
    >>> incantation['name']
    'draw energy from the Dark Dimension'
    >>> girder_connection.delete(
    ...     "item/{}".format(incantation["_id"])
    ... )['message']
    'Deleted item draw energy from the Dark Dimension.'
    >>> girder_connection.delete(
    ...     "folder/{}".format(book["_id"])
    ... )['message']
    'Deleted folder Book of Cagliostro.'
    >>> girder_connection.delete(
    ...     'collection/{}'.format(
    ...         get_girder_id_by_name(
    ...             girder_connection,
    ...             "Collection",
    ...             "Ancient One"
    ...         )
    ...     )
    ... )['message']
    'Deleted collection Ancient One.'
    """
    return(
        get_girder_id_by_name(
            girder_connection,
            x[0],
            x[1],
            parent=parent
        )
    )


def get_files_in_item(
    girder_connection,
    item_id,
    sort="created",
    sortdir=-1
):
    """
    Function to get a dictionary of Files in an Item in
    a Girder database.

    Parameters
    ----------
    girder_connection: GirderClient
        an active `GirderClient <http://girder.readthedocs.io/en/latest/python-client.html#girder_client.GirderClient>`_

    item_id: string
        Girder _id of Item.

    sort: string, optional
        Field to sort the result set by.
        default = "created"

    sortdir: int, optional
        Sort order: 1 for ascending, -1 for descending.
        default = -1

    Returns
    -------
    files: dictionary or None
        metadata of files in Girder Item

    Examples
    --------
    >>> import girder_client as gc
    >>> get_files_in_item(
    ...     girder_connection=gc.GirderClient(
    ...         apiUrl="https://data.kitware.com/api/v1/"
    ...     ),
    ...     item_id="58a372f38d777f0721a64df3"
    ... )[0]["name"]
    'Normal001-T1-Flash.mha'
    """
    return(
      girder_connection.get(
        "".join([
          "item/",
          item_id,
          "/files?",
          "sort=",
          sort,
          "&sortdir=",
          str(sortdir)
        ])
      )
    )


def get_folder_or_item_info(girder_id, girder_type, girder_connection):
    """
    Function to collect all relevant info about a Folder or Item.

    Parameters
    ----------
    girder_id: string
        Girder _id

    girder_type: string
        "Folder" or "Item"

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    info: dictionary

    Examples
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> book = find_or_create(
    ...     ("Folder", "Book of Cagliostro"),
    ...     ("Collection", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Collection",
    ...         "Ancient One"
    ...     )),
    ...     girder_connection
    ... )
    >>> get_folder_or_item_info(
    ...     book,
    ...     "Folder",
    ...     girder_connection
    ... )['name']
    'Book of Cagliostro'
    """
    info = {
        "old_ids" : [girder_id],
        **girder_connection.get(
            "{}/{}".format(
                girder_type.lower(),
                girder_id
            )
        )
    }
    return({
        key: info[key] for key in info if key not in [
            "_id",
            "_modelType",
            "baseParentId",
            "baseParentType"
        ]
    })


def get_girder_id_by_name(
    girder_connection,
    entity,
    name,
    parent=None,
    limit=1,
    sortdir=-1,
    index=0
):
    """
    Function to get the `_id` of a single entity in a Girder database.

    Parameters
    ----------
    girder_connection: GirderClient
        an active `GirderClient <http://girder.readthedocs.io/en/latest/python-client.html#girder_client.GirderClient>`_

    entity: string
        "collection", "folder", "item", "file", "user"

    name: string
        name of entity

    parent: 2-tuple, optional, default=None
        (parentType, parent_id)
        parentType: string
            "Collection", "Folder", or "User"
        parendId: string
            Girder _id for parent

    limit: int, optional, default=1
        maximum number of query results

    sortdir: int, optional, default=-1
        Sort order: 1 for ascending, -1 for descending.

    index: int, default=0
        0-indexed index of named entity in given sort order.

    Returns
    -------
    _id: string
        Girder _id of requested entity

    Examples
    --------
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> girder_connection.get(
    ...     "collection/{}".format(
    ...         get_girder_id_by_name(
    ...             girder_connection=girder_connection,
    ...             entity="Collection",
    ...             name="Ancient One"
    ...         )
    ...     )
    ... )["name"]
    'Ancient One'
    """
    entity = entity.title()
    query = "".join([
        entity.lower(),
        "?text=" if entity in {
            "Collection"
        } else "?name=",
        name,
        "&parentType={0}&parentId={1}".format(
            parent[0].lower(),
            parent[1]
        ) if (
            parent and entity!="Item"
        ) else "&folderId={0}".format(
            parent[1]
        ) if parent else "",
        "&limit=",
        str(limit),
        "&sortdir=",
        str(sortdir)
    ])
    j = json.loads(
        girder_connection.get(
            query,
            jsonResp=False
        ).content.decode(
            "UTF8"
        )
    )
    return(
        j[0]["_id"] if len(
            j
        ) else girder_connection.createCollection(
            name=name,
            public=False
        )["_id"] if entity=="Collection" else girder_connection.post(
            query
        )["_id"]
    )


def get_group_ids(
    girder_connection,
    groups={
        "Editors",
        "Managers",
        "Users",
        "Viewers"
    }
):
    """
    Function to collect Girder _ids,
    optionally creating any missing groups.

    Parameters
    ----------
    girder_connection: GirderClient
        active Girder Client

    groups: set
        set of Group names for which to get
        Girder _ids
        item: string
            Group name
        default: {
            "Editors",
            "Managers",
            "Users",
            "Viewers"
        }

    Returns
    -------
    groups: dictionary
        key: string
            name from original set
        value: string
            Girder Group _id

    Examples
    --------
    >>> import girder_client as gc
    >>> get_group_ids(
    ...     girder_connection=gc.GirderClient(
    ...         apiUrl="https://data.kitware.com/api/v1/"
    ...     ),
    ...     groups={"VIGILANT"}
    ... )
    {'VIGILANT': '58a354fe8d777f0721a6106a'}
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> groups = [k for k in get_group_ids(
    ...     girder_connection,
    ...     {"Masters of the Mystic Arts", "Sorcerers Supreme"}
    ... )]
    >>> groups.sort()
    >>> groups
    ['Masters of the Mystic Arts', 'Sorcerers Supreme']
    """
    return({
        group: get_girder_id_by_name(
            girder_connection,
            "group",
            group
            ) for group in groups
    })


def get_user_id_by_email(girder_connection, email):
    """
    Function to get the `_id` of a single User in a Girder database.

    Parameters
    ----------
    girder_connection: GirderClient
        an active `GirderClient <http://girder.readthedocs.io/en/latest/python-client.html#girder_client.GirderClient>`_

    email: string
        email address

    Returns
    -------
    _id: string or None
        Girder _id of requested User, or None if not found

    Examples
    --------
    >>> import girder_client as gc
    >>> get_user_id_by_email(
    ...     girder_connection=gc.GirderClient(
    ...         apiUrl="https://data.kitware.com/api/v1/"
    ...     ),
    ...     email="test@example.com"
    ... )
    """
    email = email.lower()
    user_ids = [
      user["_id"] for user in girder_connection.get(
            "".join([
                "user?text=",
                email
            ])
        ) if (
            (
                 "email" in user
            ) and (
                 user["email"]==email
            )
        ) or (
            (
                 "login" in user
            ) and (
                 user["login"]==email
            )
        )
    ]
    return(
        user_ids[0] if len(user_ids) else None
    )


def ls_x_in_y(x_type, y, girder_connection):
    """
    Function to list **x** in **y**.

    Parameters
    ----------
    x_type: string
        "Folder", "Item", etc.

    y: 2-tuple
        y[0]: string
            "Collection", "Folder", etc.

        y[1]: string
            Girder_id

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    x: list of dictionaries
        ≅ JSON array of objects

    Examples
    --------
    >>> import girder_client as gc
    >>> ls_x_in_y(
    ...     "Folder",
    ...     ("Collection", "58b5d21a8d777f0aef5d04b1"),
    ...     girder_connection=gc.GirderClient(
    ...         apiUrl="https://data.kitware.com/api/v1/"
    ...     )
    ... )
    [{'_accessLevel': 0, '_id': '58b5d86c8d777f0aef5d04b4', '_modelType': 'folder', 'baseParentId': '58b5d21a8d777f0aef5d04b1', 'baseParentType': 'collection', 'created': '2017-02-28T20:07:08.074000+00:00', 'creatorId': '55a413168d777f649a9ba343', 'description': '', 'name': 'TestData', 'parentCollection': 'collection', 'parentId': '58b5d21a8d777f0aef5d04b1', 'public': True, 'publicFlags': [], 'size': 41319999, 'updated': '2017-02-28T20:07:08.074000+00:00'}, {'_accessLevel': 0, '_id': '58cb12048d777f0aef5d79fc', '_modelType': 'folder', 'baseParentId': '58b5d21a8d777f0aef5d04b1', 'baseParentType': 'collection', 'created': '2017-03-16T22:30:28.994000+00:00', 'creatorId': '55a413168d777f649a9ba343', 'description': '', 'name': 'TomvizData', 'parentCollection': 'collection', 'parentId': '58b5d21a8d777f0aef5d04b1', 'public': True, 'size': 0, 'updated': '2017-03-24T18:30:21.117000+00:00'}]
    """
    api_query = "".join([
        x_type.lower(),
        "?folderId=",
        y[1]
    ]) if (
        x_type.lower()=="item" and
        y[0].lower()=="folder"
    ) else "".join([
        x_type.lower(),
        "?parentType=",
        y[0].lower(),
        "&parentId=",
        y[1]
    ])
    return(
        girder_connection.get(
            api_query
        )
    )


def move_item_to_folder(girder_id, girder_connection):
    """
    Function to collect all relevant info about a Folder or Item.

    Parameters
    ----------
    girder_id: string
        Item's Girder_id

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    folder_id: string
        Girder_id for new Folder replacing old Item

    Examples
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> collection = get_girder_id_by_name(
    ...     girder_connection,
    ...     "Collection",
    ...     "Ancient One"
    ... )
    >>> item = get_girder_id_by_name(
    ...     girder_connection,
    ...     "Item",
    ...     "Kaecilius",
    ...     ("Folder", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Folder",
    ...         "Masters of the Mystic Arts",
    ...         ("Collection", collection)
    ...     ))
    ... )
    >>> from urllib.request import urlopen
    >>> image_stream = urlopen(
    ...     "/".join([
    ...         "https://vignette.wikia.nocookie.net",
    ...         "marvelcinematicuniverse/images/1/14/",
    ...         "DS_Kaecilius_Poster_cropped.png"
    ...     ])
    ... )
    >>> img_id = girder_connection.uploadFile(
    ...     parentId=item,
    ...     parentType="item",
    ...     stream=image_stream,
    ...     name="Kaecilius.png",
    ...     size=int(
    ...         image_stream.info()["Content-Length"]
    ...     )
    ... )["_id"]
    >>> folder = move_item_to_folder(item, girder_connection)
    >>> girder_connection.get(
    ...     "folder/{}".format(folder)
    ... )['_modelType']
    'folder'
    """
    info = get_folder_or_item_info(
        girder_id,
        "Item",
        girder_connection
    )
    files = girder_connection.get(
        "item/{}/files".format(girder_id)
    )
    if len(files):
        if not os.path.exists("temp_filestore"):
            os.makedirs("temp_filestore")
        for file in files:
            girder_connection.downloadFile(
                file["_id"],
                os.path.join(
                    os.getcwd(),
                    "temp_filestore",
                    file["name"]
                )
            )
    girder_connection.delete("item/{}".format(info['old_ids'][0]))
    folder_id = girder_connection.post(
        "&".join([
            "folder?name={}".format(
                info['name']
            ),
            "parentId={}".format(info['folderId']),
            "parentType=folder",
            "reuseExisting=true",
            "metadata={}".format(
                quote(
                    json.dumps(
                        info['meta'] if 'meta' in info else {}
                    )
                )
            ),
            "description={}".format(
                info['description']
            ) if 'description' in info else ''
        ])
    )["_id"]
    if len(files):
        for file in files:
            image_stream = urlopen("/".join([
                "file://",
                os.getcwd(),
                "temp_filestore",
                file["name"]
            ])) # url_or_filepath includes protocol, eg, "https://", "file://", "ftp://"

            img_id = girder_connection.uploadFile(
                parentId=folder_id,
                parentType="folder",
                stream=image_stream,
                name=".".join([
                    file["name"]
                ]), # name to save the File as in Mindlogger, including extension
                size=int(
                    image_stream.info()["Content-Length"]
                ) # size of the File in bytes
            )["_id"]
            os.remove(os.path.join(
                "temp_filestore",
                file["name"]
            ))
        os.removedirs("temp_filestore")
    return(folder_id)


def mv(
    x,
    new_parent,
    girder_connection
):
    """
    Function to move a Girder entity to a new_parent.

    Parameters
    ----------
    x: 2-tuple
        x[0]: string
            "Folder", "Item", etc.
        x[1]: string
            Girder_id

    new_parent: 2-tuple
        new_parent[0]: string
            "Collection", "Folder", etc.
        new_parent[1]: string
            Girder_id

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    x_object: dictionary
        ≅JSON representation of entity in new location

    Examples
    --------
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> book = find_or_create(
    ...     ("Folder", "Book of Cagliostro"),
    ...     ("Collection", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Collection",
    ...         "Ancient One"
    ...     )),
    ...     girder_connection
    ... )
    >>> incantation = find_or_create(
    ...     ("Item", "draw energy from the Dark Dimension"),
    ...     ("Folder", book),
    ...     girder_connection
    ... )
    >>> girder_connection.get("folder/{}".format(mv(
    ...     ("Item", incantation),
    ...     ("Folder", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Folder",
    ...         "Incantations",
    ...         ("User", get_user_id_by_email(
    ...             girder_connection,
    ...             "wong@wong.wong"
    ...         ))
    ...     )),
    ...     girder_connection
    ... )['folderId']))['name']
    'Incantations'
    """
    api_query = "".join([
        x[0].lower(),
        "/",
        x[1],
        "?folderId=",
        new_parent[1]
    ]) if (
        x[0].lower()=="item" and
        new_parent[0].lower()=="folder"
    ) else "".join([
        x[0].lower(),
        "/",
        x[1],
        "?parentId=",
        new_parent[1],
        "&parentType=",
        new_parent[0].lower()
    ])
    return(
        girder_connection.put(
            api_query
        )
    )


def rename(
    x,
    new_name,
    girder_connection
):
    """
    Function to rename a Girder entity.

    Parameters
    ----------
    x: 2-tuple
        x[0]: string
            "Folder", "Item", etc.
        x[1]: string
            Girder_id

    new_name: string
        new name for entity

    girder_connection: GirderClient
        active GirderClient

    Returns
    -------
    x_object: dictionary
        ≅JSON representation of entity in new location

    Examples
    --------
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> book = find_or_create(
    ...     ("Folder", "Book of Cagliostro"),
    ...     ("Collection", get_girder_id_by_name(
    ...         girder_connection,
    ...         "Collection",
    ...         "Ancient One"
    ...     )),
    ...     girder_connection
    ... )
    >>> incantation = find_or_create(
    ...     ("Item", "draw energy from the Dark Dimension"),
    ...     ("Folder", book),
    ...     girder_connection
    ... )
    >>> rename(
    ...     ("Item", incantation),
    ...     "Draw Energy",
    ...     girder_connection
    ... )['name']
    'Draw Energy'
    """
    api_query = "".join([
        x[0].lower(),
        "/",
        x[1],
        "?name=",
        new_name
    ])
    return(
        girder_connection.put(
            api_query
        )
    )


def _delete_collections(girder_connection, except_collection_ids):
    """
    Function to delete all collections
    except those collection_ids specified
    as exceptions.

    Parameters
    ----------
    gc: GirderClient

    except_collection_ids: iterable
        list, set, or tuple of collection_ids to
        keep. Can be empty.

    Returns
    -------
    collections_kept_and_deleted: DataFrame
        DataFrame of Collections kept and deleted

    Examples
    --------
    >>> import os
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> ancientOne = get_girder_id_by_name(
    ...     girder_connection,
    ...     "Collection",
    ...     "Ancient One"
    ... )
    >>> deletion_table = _delete_collections(
    ...     girder_connection,
    ...     [c["_id"] for c in girder_connection.get(
    ...         "collection"
    ...     ) if c["name"] != 'Ancient One']
    ... )
    >>> deletion_table[
    ...     deletion_table["name"]=="Ancient One"
    ... ]["deleted"].values[0]
    True
    """
    except_collection_ids = except_collection_ids if isiterable(
        except_collection_ids
    ) else {}
    kept = pd.DataFrame(
      [
        {
            **girder_connection.getCollection(
                i["_id"]
            ),
            "deleted": False
        } for i in girder_connection.listCollection(
        ) if i["_id"] in except_collection_ids
      ]
    )
    deleted = pd.DataFrame(
      [
        {
            **girder_connection.getCollection(
                i["_id"]
            ),
            "deleted": True
        } for i in girder_connection.listCollection(
        ) if i["_id"] not in except_collection_ids
      ]
    )
    collections_kept_and_deleted = pd.concat(
        [
            kept,
            deleted
        ],
        ignore_index = True
    )
    if "deleted" in collections_kept_and_deleted.columns:
        for u in collections_kept_and_deleted[
            collections_kept_and_deleted[
                "deleted"
            ]==True
        ]["_id"]:
            girder_connection.delete(
                "collection/{0}".format(
                    u
                )
            )
    return(
        collections_kept_and_deleted
    )


def _delete_users(girder_connection, except_user_ids):
    """
    Function to delete all users
    except those user_ids specified
    as exceptions.

    Parameters
    ----------
    girder_connection: GirderClient

    except_user_ids: iterable
        list, set, or tuple of user_ids to
        keep. Can be empty.

    Returns
    -------
    users_kept_and_deleted: DataFrame
        DataFrame of Users kept and deleted


    Examples
    --------
    >>> import os
    >>> import random
    >>> import string
    >>> from .. import girder_connections
    >>> which_girder = "dev"
    >>> config, context, api_url = girder_connections.configuration(
    ...     config_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "config.json.template"
    ...     ),
    ...     context_file=os.path.join(
    ...         os.path.dirname(__file__),
    ...         "context.json"
    ...     ),
    ...     which_girder=which_girder
    ... )
    >>> which_girder = "girder-{}".format(which_girder)
    >>> girder_connection = girder_connections.connect_to_girder(
    ...     api_url=api_url,
    ...     authentication=(
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"],
    ...         config[which_girder]["APIkey"]
    ...     ) if "APIkey" in config[which_girder] else (
    ...         config[which_girder]["user"],
    ...         config[which_girder]["password"]
    ...     )
    ... )
    Connected to the Girder database 🏗🍃 and authenticated.
    >>> dormammu = get_user_id_by_email(
    ...     girder_connection,
    ...     "dormammu@wong.wong"
    ... )
    >>> dormammu = dormammu if dormammu else girder_connection.post(
    ...     "&".join([
    ...         "user?login=dormammu",
    ...         "email=dormammu@wong.wong",
    ...         "firstName=Dormammu",
    ...         "lastName=Dormammu",
    ...         "password={}".format(
    ...             "".join(random.sample(
    ...                 (string.ascii_letters+string.digits)*100,
    ...                 12
    ...             ))
    ...         )
    ...     ])
    ... )["_id"]
    >>> deletion_table = _delete_users(
    ...     girder_connection,
    ...     [u["_id"] for u in girder_connection.get(
    ...         "user"
    ...     ) if u["login"]!="dormammu"]
    ... )
    >>> deletion_table[
    ...     deletion_table["login"]=="wongwongwong"
    ... ]["deleted"].values[0]
    False
    """
    except_user_ids = except_user_ids if isiterable(
        except_user_ids
    ) else {}
    kept = pd.DataFrame(
        [
           {
                **girder_connection.getUser(
                    i["_id"]
                ),
                "deleted": False
            } for i in girder_connection.listUser(
            ) if i["_id"] in except_user_ids
        ]
    )
    deleted = pd.DataFrame(
        [
            {
                **girder_connection.getUser(
                    i["_id"]
                ),
                "deleted": True
            } for i in girder_connection.listUser(
            ) if i["_id"] not in except_user_ids
        ]
    )
    users_kept_and_deleted = pd.concat(
        [
            kept,
            deleted
        ],
        ignore_index = True
    )
    for u in users_kept_and_deleted[
        users_kept_and_deleted[
            "deleted"
        ]==True
    ]["_id"]:
        girder_connection.delete(
            "user/{0}".format(
                u
            )
        )
    return(
        users_kept_and_deleted
    )
