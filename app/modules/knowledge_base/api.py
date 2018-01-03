from app.models.models import Politician, Party
from sqlalchemy import or_, func

from app.modules.common.utils import collection_as_dict


def find_politician(id):
    politician = Politician.query.filter(Politician.system_id == id).first()
    if politician:
        return {'politician': politician.as_dict() }
    else:
        return {'message' : 'Politician not found.'}


def find_party(name):
    parties = Party.query.filter(
        or_(func.lower(Party.abbreviation) == func.lower(name), func.lower(Party.name) == func.lower(name))).all()

    if len(parties) > 0:
        return {'parties': collection_as_dict(parties)}
    else:
        return {'message' : 'No political parties found.'}
