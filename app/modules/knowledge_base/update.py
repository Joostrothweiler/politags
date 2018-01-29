import logging

from app import db
from app.models.models import Politician
from app.modules.common.utils import parse_human_name
from app.modules.knowledge_base.get_almanak import get_all_current_ministers, get_all_current_local_politicians
from app.modules.knowledge_base.get_kamerleden import get_all_current_members_of_chamber

logger = logging.getLogger('update')

def update_knowledge_base():
    update_members_of_chamber()
    update_ministers()
    update_local_politicians()

def update_local_politicians():
    local_politicians = get_all_current_local_politicians()
    # 'system_id', 'full_name', 'party', 'municipality', 'role'
    # TODO: Parse into db format

def update_ministers():
    ministers = get_all_current_ministers()
    # 'system_id', 'full_name', 'department', 'role'
    # TODO: Parse into db format

def update_members_of_chamber():
    chamber_members = get_all_current_members_of_chamber()
    # 'system_id', 'title', 'initials', 'middle_name', 'last_name', 'first_name', 'first_name_alt', 'role', 'party',
    #TODO: Parse into db format


def find_or_create_politician(system_id, title, first_name, last_name, suffix, party, municipality, role):
    """ Find existing politicians or create new one """
    politician = Politician.query.filter(Politician.last_name == last_name) \
        .filter(Politician.first_name == first_name) \
        .filter(Politician.party == party).first()

    if not politician:
        politician = Politician(system_id=system_id, title=title, first_name=first_name, last_name=last_name,
                                suffix=suffix, party=party, municipality=municipality, role=role)
        db.session.add(politician)
    return politician