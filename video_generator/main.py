from . import _0_general , _80_netlify_depolyment
import config

sujet = config.SUJET
langues = config.LANGUES

_0_general.lanceur(sujet, langues)
#_80_netlify_depolyment.deploy_videos()