## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2011-2012, 2015, 2019-2021, 2024 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2012, 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
#
# This file is part of "Metastreams Harvester"
#
# "Metastreams Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Metastreams Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Metastreams Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from os.path import join, abspath, dirname, isdir
from os import makedirs
from sys import stdout
from xml.sax.saxutils import escape as escapeXml
from io import StringIO
from lxml.etree import parse
from meresco.xml import xpathFirst

from weightless.io import Reactor
from weightless.core import compose, be

from meresco.components.json import JsonDict
from meresco.core import Observable, Transparent

from meresco.html import DynamicHtml
from meresco.html.login import BasicHtmlLoginForm, SecureZone, UserFromSession
from seecr.zulutime import ZuluTime

from meresco.components.log import LogCollector, ApacheLogWriter, HandleRequestLog
from meresco.components.http import (
    PathFilter,
    ObservableHttpServer,
    StringServer,
    BasicHttpHandler,
    SessionHandler,
    CookieMemoryStore,
    StaticFiles,
    Deproxy,
)
from meresco.components.http.utils import ContentTypePlainText, okPlainText

from .__version__ import VERSION_STRING, VERSION
from .repositorystatus import RepositoryStatus
from .harvesterdataactions import HarvesterDataActions
from .apiactions import ApiActions
from .harvesterdataretrieve import HarvesterDataRetrieve
from .timeslot import Timeslot
from meresco.components.http.utils import ContentTypeJson
from .throughputanalyser import ThroughputAnalyser
from .onlineharvest import OnlineHarvest
from .filterfields import FilterFields
from .environment import createEnvironment

from metastreams.users import initializeUserGroupManagement

from time import localtime, strftime, time
from uuid import uuid4
from json import dumps

import importlib

myPath = dirname(abspath(__file__))
usrSharePath = "/usr/share/metastreams"
usrSharePath = join(dirname(dirname(myPath)), "usr-share")  # DO_NOT_DISTRIBUTE
dynamicHtmlPath = join(myPath, "controlpanel", "dynamic")
staticHtmlPath = join(usrSharePath, "controlpanel")


def dateSince(days):
    return strftime("%Y-%m-%d", localtime(time() - days * 3600 * 24))


def dna(
    reactor,
    port,
    dataPath,
    logPath,
    statePath,
    externalUrl,
    customerLogoUrl,
    deproxyIps=None,
    deproxyIpRanges=None,
    addons=None,
    **ignored,
):
    environment = createEnvironment(dataPath)
    harvesterData = environment.createHarvesterData()
    harvesterDataRetrieve = environment.createHarvesterDataRetrieve()
    deproxy = Deproxy(deproxyForIps=deproxyIps, deproxyForIpRanges=deproxyIpRanges)
    repositoryStatus = be((RepositoryStatus(logPath, statePath), (harvesterData,)))
    configDict = JsonDict(
        logPath=logPath,
        statePath=statePath,
        externalUrl=externalUrl,
        dataPath=dataPath,
    )
    print("Started Metastreams with configuration:\n" + configDict.pretty_print())

    userGroup = initializeUserGroupManagement(join(statePath, "users"), harvesterData)
    basicHtmlLoginHelix = (
        BasicHtmlLoginForm(
            action="/login.action",
            loginPath="/login",
            home="/index",
            rememberMeCookie=False,
            lang="nl",
        ),
        (userGroup.basicHtmlObserver,),
    )
    varWwwdataPath = join(statePath, "www-data", "var")
    isdir(varWwwdataPath) or makedirs(varWwwdataPath)

    staticFilePaths = []
    staticFiles = Transparent()
    for path, libdir in [
        ("/js/bootstrap", "/usr/share/javascript/bootstrap5/js"),
        ("/css/bootstrap", "/usr/share/javascript/bootstrap5/css"),
        ("/css/bootstrap-icons", "/usr/share/javascript/bootstrap-icons"),
        ("/js/jquery", "/usr/share/javascript/jquery"),
        ("/js/jquery-tablesorter", "/usr/share/javascript/jquery-tablesorter"),
        ("/css/jquery-tablesorter", "/usr/share/javascript/jquery-tablesorter/css"),
        ("/js/autosize", "/usr/share/javascript/autosize"),
        ("/static", staticHtmlPath),
        ("/var", varWwwdataPath),
    ]:
        staticFiles.addObserver(StaticFiles(libdir=libdir, path=path))
        staticFilePaths.append(path)

    addons = addons or []
    addon_mods = []
    for addon in addons:
        addon_mod = importlib.import_module(addon)
        addon_mods.append(addon_mod)

    securezone_excluded = [
        "/index",
        "/invalid",
        "/rss",
        "/running.rss",
        "/showHarvesterStatus",
        "/login/dialog/show",
    ]
    for addon in addon_mods:
        if hasattr(addon, "securezone_excluded"):
            securezone_excluded.extend(addon.securezone_excluded)

    additionalGlobals = {
        "externalUrl": externalUrl,
        "escapeXml": escapeXml,
        "compose": compose,
        "dumps": dumps,
        "VERSION": VERSION,
        "CONFIG": configDict,
        "Timeslot": Timeslot,
        "ThroughputAnalyser": ThroughputAnalyser,
        "dateSince": dateSince,
        "callable": callable,
        "OnlineHarvest": OnlineHarvest,
        "StringIO": StringIO,
        "okPlainText": okPlainText,
        "ZuluTime": ZuluTime,
        "xpathFirst": xpathFirst,
        "customerLogoUrl": customerLogoUrl,
        "uuid": lambda: str(uuid4()),
    }
    for addon in addon_mods:
        if hasattr(addon, "additionalGlobals"):
            for name, value in addon.additionalGlobals.items():
                if name in additionalGlobals:
                    print(f"addon {addon} overwrites additionalGlobal {name}")
                additionalGlobals[name] = value

    def get_addon_hook(name, default):
        for addon in addon_mods:
            if (hooks := getattr(addon, "hooks", None)) is not None:
                if isinstance(hooks, dict):
                    if (hook := hooks.get(name)) is not None:
                        return hook
        return default

    additionalGlobals["get_addon_hook"] = get_addon_hook

    return (
        Observable(),
        (
            ObservableHttpServer(reactor, port),
            (
                LogCollector(),
                (ApacheLogWriter(stdout),),
                (
                    deproxy,
                    (
                        HandleRequestLog(),
                        (
                            BasicHttpHandler(),
                            (
                                SessionHandler(),
                                (
                                    CookieMemoryStore(
                                        name="meresco-harvester", timeout=2 * 60 * 60
                                    ),
                                ),
                                (
                                    UserFromSession(),
                                    (
                                        PathFilter("/info/version"),
                                        (
                                            StringServer(
                                                VERSION_STRING, ContentTypePlainText
                                            ),
                                        ),
                                    ),
                                    (
                                        PathFilter("/info/config"),
                                        (
                                            StringServer(
                                                configDict.dumps(), ContentTypeJson
                                            ),
                                        ),
                                    ),
                                    (PathFilter("/login.action"), basicHtmlLoginHelix),
                                    (
                                        PathFilter("/api"),
                                        (ApiActions(), (harvesterData,)),
                                    ),
                                    (staticFiles,),
                                    (
                                        PathFilter(
                                            "/",
                                            excluding=[
                                                "/info/version",
                                                "/info/config",
                                                "/action",
                                                "/api",
                                                "/login.action",
                                            ]
                                            + harvesterDataRetrieve.paths
                                            + staticFilePaths,
                                        ),
                                        (
                                            SecureZone(
                                                "/login",
                                                excluding=securezone_excluded,
                                                defaultLanguage="nl",
                                            ),
                                            (
                                                PathFilter(
                                                    "/",
                                                    excluding=userGroup.excludedPaths,
                                                ),
                                                (
                                                    DynamicHtml(
                                                        [dynamicHtmlPath]
                                                        + [
                                                            addon.dynamic_path
                                                            for addon in addon_mods
                                                        ],
                                                        reactor=reactor,
                                                        additionalGlobals=additionalGlobals,
                                                        indexPage="/index",
                                                    ),
                                                    basicHtmlLoginHelix,
                                                    (harvesterData,),
                                                    (repositoryStatus,),
                                                    (userGroup.dynamicHtmlObserver,),
                                                ),
                                            ),
                                            (userGroup.actions,),
                                        ),
                                    ),
                                    (
                                        PathFilter("/action"),
                                        (HarvesterDataActions(), (harvesterData,)),
                                    ),
                                    (
                                        PathFilter(harvesterDataRetrieve.paths),
                                        (
                                            harvesterDataRetrieve,
                                            (
                                                FilterFields(),
                                                (harvesterData,),
                                            ),
                                            (repositoryStatus,),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def startServer(port, **kwargs):
    reactor = Reactor()
    server = be(dna(reactor, port, **kwargs))
    list(compose(server.once.observer_init()))

    print("Ready to rumble at", port)
    stdout.flush()
    reactor.loop()
