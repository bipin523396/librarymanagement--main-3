"""Template globals for URLs that work on Vercel, Render, and localhost."""


def site_urls(request):
  lang = getattr(request, 'LANGUAGE_CODE', None) or 'en'
  prefix = f'/{lang}/library'
  return {
    'LIBRARY_URL_PREFIX': prefix,
  }
