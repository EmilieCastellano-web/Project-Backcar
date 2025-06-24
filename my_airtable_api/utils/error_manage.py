"""
Utilitaires pour la gestion des erreurs de template et autres fonctions d'aide
"""
import logging
from django.shortcuts import render
from functools import wraps
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError

logger = logging.getLogger(__name__)


def handle_template_errors(error_template='error.html'):
    """
    Décorateur pour gérer automatiquement les erreurs de template
    et rediriger vers une page d'erreur personnalisée
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except (TemplateDoesNotExist, TemplateSyntaxError) as e:
                logger.error(f"Template error in {view_func.__name__}: {str(e)}")
                return render(request, error_template, {
                    'error': f"Erreur de template : {str(e)}",
                    'template_error': True,
                    'error_type': 'template_syntax_error',
                    'view_name': view_func.__name__
                })
            except Exception as e:
                logger.error(f"Unexpected error in {view_func.__name__}: {str(e)}")
                return render(request, error_template, {
                    'error': str(e),
                    'template_error': True,
                    'error_type': 'unexpected_error',
                    'view_name': view_func.__name__
                })
        return wrapper
    return decorator


def render_with_error_handling(request, template_name, context=None, error_template='error.html'):
    """
    Fonction utilitaire pour rendre un template avec gestion automatique des erreurs
    """
    try:
        return render(request, template_name, context or {})
    except (TemplateDoesNotExist, TemplateSyntaxError) as e:
        logger.error(f"Template error with {template_name}: {str(e)}")
        return render(request, error_template, {
            'error': f"Erreur de template : {str(e)}",
            'template_error': True,
            'error_type': 'template_syntax_error',
            'template_name': template_name
        })
    except Exception as e:
        logger.error(f"Unexpected error rendering {template_name}: {str(e)}")
        return render(request, error_template, {
            'error': str(e),
            'template_error': True,
            'error_type': 'unexpected_error',
            'template_name': template_name
        })
