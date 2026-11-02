{#- Cover page of the generated PDF (mkdocs-print-site-plugin). -#}
<div class="px-cover">
  <img class="px-cover__logo" src="../assets/proteus-logo-color.png" alt="PROTEUS – The Copernicus Agent">
  <p class="px-cover__tagline">The Copernicus Agent for Next-Generation Environmental Intelligence</p>
  <h1 class="px-cover__title">Responsible AI Guideline</h1>
  <p class="px-cover__meta">
    Version {{ config.extra.version }} – {{ config.extra.release_date }}<br>
    DOI: {{ config.extra.doi }}<br>
    {{ config.site_url }}
  </p>
  <div class="px-cover__funding">
    <img src="../assets/eu-flag.png" alt="Flag of the European Union">
    <p>Funded by the European Union under GA No. {{ config.extra.grant }}.
      Views and opinions expressed are however those of the author(s) only and do
      not necessarily reflect those of the European Union or HaDEA. Neither the
      European Union nor the granting authority can be held responsible for them.
      Text licensed under CC BY 4.0.</p>
  </div>
</div>
