"""
Tests pour la gestion des erreurs de template
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from mission.views.list_views import mission_form_view
from my_airtable_api.utils.error_manage import render_with_error_handling, handle_template_errors
from django.template.exceptions import TemplateDoesNotExist


class TemplateErrorHandlingTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_render_with_error_handling_template_not_found(self):
        """Test que render_with_error_handling gère les templates inexistants"""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        # Tenter de rendre un template inexistant
        response = render_with_error_handling(
            request, 
            'template_inexistant.html', 
            {'test': 'value'}
        )
        
        # Vérifier que la réponse utilise le template d'erreur
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'template_error')
        self.assertContains(response, 'template_syntax_error')

    def test_mission_form_view_with_decorator(self):
        """Test que le décorateur handle_template_errors fonctionne"""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        # Appeler la vue qui utilise le décorateur
        response = mission_form_view(request)
        
        # La vue devrait fonctionner normalement
        self.assertEqual(response.status_code, 200)

    def test_error_template_context(self):
        """Test que le template d'erreur reçoit les bonnes variables"""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        response = render_with_error_handling(
            request, 
            'template_inexistant.html', 
            {'test': 'value'}
        )
        
        # Vérifier le contexte de la réponse
        context = response.context
        self.assertTrue(context['template_error'])
        self.assertEqual(context['error_type'], 'template_syntax_error')
        self.assertEqual(context['template_name'], 'template_inexistant.html')
        self.assertIn('error', context)
