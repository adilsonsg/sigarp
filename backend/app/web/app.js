const API = "/api/v1";
const state = {
  token: sessionStorage.getItem("sigarp_token") || "",
  page: 1,
  pageData: null,
  filters: {},
  view: "opportunities",
};

const elements = {
  accessPanel: document.querySelector("#access-panel"),
  workspace: document.querySelector("#workspace"),
  accessForm: document.querySelector("#access-form"),
  accessError: document.querySelector("#access-error"),
  token: document.querySelector("#token"),
  changeToken: document.querySelector("#change-token"),
  connectionDot: document.querySelector("#connection-dot"),
  identityLabel: document.querySelector("#identity-label"),
  filters: document.querySelector("#filters"),
  consultationView: document.querySelector("#consultation-view"),
  clearFilters: document.querySelector("#clear-filters"),
  cards: document.querySelector("#cards"),
  status: document.querySelector("#status"),
  resultSummary: document.querySelector("#result-summary"),
  pageLabel: document.querySelector("#page-label"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  exportCsv: document.querySelector("#export-csv"),
  dialog: document.querySelector("#details-dialog"),
  detailsTitle: document.querySelector("#details-title"),
  detailsContent: document.querySelector("#details-content"),
  closeDetails: document.querySelector("#close-details"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function displayLabel(value) {
  if (!value) return "Não informado";
  return String(value)
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function formatDate(value) {
  if (!value) return "Não informada";
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short" }).format(
    new Date(value),
  );
}

function formatNumber(value) {
  if (value === null || value === undefined) return "Não informada";
  return new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function formatCurrency(value) {
  if (value === null || value === undefined) return "Não informado";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));
}

function safeExternalUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

async function apiFetch(path) {
  const response = await fetch(`${API}${path}`, {
    headers: { Authorization: `Bearer ${state.token}` },
  });
  if (response.status === 401 || response.status === 403) {
    throw new Error(
      response.status === 401 ? "Token inválido ou ausente." : "Acesso não autorizado.",
    );
  }
  if (!response.ok) {
    throw new Error(`Falha na consulta (HTTP ${response.status}).`);
  }
  return response.json();
}

function showAccess() {
  elements.workspace.classList.add("hidden");
  elements.accessPanel.classList.remove("hidden");
  elements.connectionDot.classList.remove("online");
  elements.identityLabel.textContent = "Não conectado";
  elements.token.value = "";
  elements.token.focus();
}

async function connect(token) {
  state.token = token.trim();
  const identity = await apiFetch("/auth/me");
  sessionStorage.setItem("sigarp_token", state.token);
  elements.identityLabel.textContent = `${identity.name} · ${displayLabel(identity.role)}`;
  elements.connectionDot.classList.add("online");
  elements.accessPanel.classList.add("hidden");
  elements.workspace.classList.remove("hidden");
  elements.accessError.textContent = "";
  await loadOpportunities();
}

function collectFilters() {
  const data = new FormData(elements.filters);
  const filters = {};
  for (const [key, value] of data.entries()) {
    const normalized = key === "uf" ? value.trim().toUpperCase() : value.trim();
    if (normalized) filters[key] = normalized;
  }
  return filters;
}

function queryString(page, pageSize = null) {
  const params = new URLSearchParams({
    ...state.filters,
    page: String(page),
  });
  if (pageSize) params.set("page_size", String(pageSize));
  return params.toString();
}

function badgeClass(value) {
  if (!value) return "badge neutral";
  if (value.includes("INCOMPATIVEL") || value.includes("ANALISE")) {
    return "badge warning";
  }
  return "badge";
}

function cardTemplate(item) {
  if (state.view === "registries") return registryCardTemplate(item);
  const sourceUrl = safeExternalUrl(item.link_sistema_origem);
  const origin = sourceUrl
    ? `<a class="origin-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">Abrir no portal de origem</a>`
    : "<span>Link de origem indisponível</span>";
  return `
    <article class="opportunity-card">
      <div class="card-top">
        <div class="meta-row">
          <strong>${escapeHtml(item.numero_controle_pncp)}</strong>
          <span>${escapeHtml(item.uf || "UF não informada")}</span>
          <span>${escapeHtml(item.municipio || "")}</span>
          <span>${escapeHtml(formatDate(item.data_publicacao_pncp))}</span>
        </div>
        <div>
          <span class="${badgeClass(item.classificacao)}">${escapeHtml(displayLabel(item.classificacao))}</span>
          <span class="${badgeClass(item.adequacao_perfil)}">${escapeHtml(displayLabel(item.adequacao_perfil))}</span>
        </div>
      </div>
      <h3 class="card-title">${escapeHtml(item.objeto_compra)}</h3>
      <div class="meta-row">
        <span>${escapeHtml(item.orgao_razao_social || "Órgão não informado")}</span>
        <span>Pontuação: ${escapeHtml(item.pontuacao)}</span>
        <span>Adequação: ${escapeHtml(item.pontuacao_adequacao ?? "—")}</span>
        <span>Revisão: ${escapeHtml(displayLabel(item.revisao_status))}</span>
      </div>
      <div class="card-footer">
        ${origin}
        <button class="details-button" type="button" data-assessment-id="${item.assessment_id}">Ver detalhes</button>
      </div>
    </article>
  `;
}

function registryCardTemplate(item) {
  const itemSummary = item.itens?.length
    ? item.itens
        .slice(0, 3)
        .map(
          (entry) => `
            <div class="registry-item-summary">
              <strong>Item ${escapeHtml(entry.numero_item)} · ${escapeHtml(displayLabel(entry.disponibilidade))}</strong>
              <span>${escapeHtml(entry.descricao)}</span>
              <span>
                Registrada: ${escapeHtml(formatNumber(entry.quantidade_registrada))}
                · Empenhada: ${escapeHtml(formatNumber(entry.quantidade_empenhada))}
                · Saldo estimado: ${escapeHtml(formatNumber(entry.saldo_estimado))}
                · Limite de adesão: ${escapeHtml(formatNumber(entry.limite_adesao))}
              </span>
            </div>
          `,
        )
        .join("")
    : '<p class="item-warning">Itens ainda não enriquecidos ou sem correspondência para os filtros.</p>';
  return `
    <article class="opportunity-card">
      <div class="card-top">
        <div class="meta-row">
          <strong>${escapeHtml(item.numero_ata || item.numero_controle_pncp)}</strong>
          <span>${escapeHtml(item.orgao.uf || "UF não informada")}</span>
          <span>Vigência: ${escapeHtml(formatDate(item.vigencia_inicio))} a ${escapeHtml(formatDate(item.vigencia_fim))}</span>
        </div>
        <div>
          <span class="badge">${escapeHtml(displayLabel(item.situacao))}</span>
          <span class="badge neutral">${escapeHtml(displayLabel(item.orgao.esfera))}</span>
          <span class="${item.possibilidade_adesao ? "badge" : "badge warning"}">${item.possibilidade_adesao ? "Adesão indicada" : "Adesão não confirmada"}</span>
        </div>
      </div>
      <h3 class="card-title">${escapeHtml(item.objeto)}</h3>
      <div class="meta-row">
        <span>${escapeHtml(item.orgao.nome)}</span>
        <span>CNPJ: ${escapeHtml(item.orgao.cnpj || "não informado")}</span>
        <span>${escapeHtml(item.itens_quantidade)} item(ns) armazenado(s)</span>
      </div>
      <div class="registry-items">${itemSummary}</div>
      <div class="card-footer">
        <span>${escapeHtml(item.numero_controle_pncp)}</span>
        <button class="details-button" type="button" data-registry-id="${item.id}">Ver detalhes</button>
      </div>
    </article>
  `;
}

function renderPage(data) {
  state.pageData = data;
  const itemName = state.view === "registries" ? "ata(s)" : "oportunidade(s)";
  elements.resultSummary.textContent = `${data.total} ${itemName} encontrada(s)`;
  elements.pageLabel.textContent = `Página ${data.page} de ${Math.max(data.total_pages, 1)}`;
  elements.previousPage.disabled = data.page <= 1;
  elements.nextPage.disabled = data.page >= data.total_pages;
  elements.exportCsv.disabled = data.total === 0;
  elements.cards.innerHTML = data.items.map(cardTemplate).join("");
  elements.status.textContent =
    data.items.length === 0 ? "Nenhum resultado para os filtros informados." : "";
}

async function loadOpportunities() {
  const endpoint =
    state.view === "registries" ? "/atas" : "/pncp/oportunidades";
  elements.status.textContent =
    state.view === "registries"
      ? "Consultando atas vigentes…"
      : "Consultando oportunidades…";
  elements.cards.innerHTML = "";
  try {
    const data = await apiFetch(`${endpoint}?${queryString(state.page)}`);
    renderPage(data);
  } catch (error) {
    elements.status.textContent = error.message;
    if (error.message.includes("Token") || error.message.includes("autorizado")) {
      sessionStorage.removeItem("sigarp_token");
      showAccess();
      elements.accessError.textContent = error.message;
    }
  }
}

function detailList(title, values) {
  if (!values?.length) return "";
  return `
    <section class="detail-section">
      <h3>${escapeHtml(title)}</h3>
      <ul>${values.map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul>
    </section>
  `;
}

function openDetails(item) {
  elements.detailsTitle.textContent = item.numero_controle_pncp;
  const items = item.itens?.map(
    (entry) =>
      `Item ${entry.numero_item}: ${entry.descricao}` +
      (entry.quantidade ? ` — ${entry.quantidade} ${entry.unidade_medida || ""}` : ""),
  );
  const documents = item.documentos?.map(
    (document) =>
      `${document.titulo || document.nome_arquivo || `Documento ${document.sequencial_documento}`}` +
      ` — ${displayLabel(document.extracao_status)}`,
  );
  elements.detailsContent.innerHTML = `
    <div class="detail-grid">
      <div class="detail-block"><small>Órgão</small>${escapeHtml(item.orgao_razao_social || "Não informado")}</div>
      <div class="detail-block"><small>Local</small>${escapeHtml([item.municipio, item.uf].filter(Boolean).join(" / ") || "Não informado")}</div>
      <div class="detail-block"><small>Publicação</small>${escapeHtml(formatDate(item.data_publicacao_pncp))}</div>
      <div class="detail-block"><small>Classificação</small>${escapeHtml(displayLabel(item.classificacao))}</div>
      <div class="detail-block"><small>Adequação</small>${escapeHtml(displayLabel(item.adequacao_perfil))}</div>
      <div class="detail-block"><small>Perfil / analisador</small>${escapeHtml(item.perfil_versao)} / ${escapeHtml(item.analisador_versao)}</div>
    </div>
    <section class="detail-section">
      <h3>Objeto</h3>
      <p>${escapeHtml(item.objeto_compra)}</p>
    </section>
    ${detailList("Termos encontrados", item.termos_encontrados)}
    ${detailList("Requisitos atendidos", item.requisitos_atendidos)}
    ${detailList("Requisitos não atendidos", item.requisitos_nao_atendidos)}
    ${detailList("Requisitos não comprovados", item.requisitos_nao_comprovados)}
    ${detailList("Itens", items)}
    ${detailList("Documentos", documents)}
    <section class="detail-section">
      <h3>Revisão humana</h3>
      <p>${escapeHtml(displayLabel(item.revisao_status))}${item.revisado_por ? ` · ${escapeHtml(item.revisado_por)}` : ""}</p>
    </section>
  `;
  elements.dialog.showModal();
}

function openRegistryDetails(item) {
  elements.detailsTitle.textContent =
    item.numero_ata || item.numero_controle_pncp;
  elements.detailsContent.innerHTML = `
    <div class="detail-grid">
      <div class="detail-block"><small>Órgão gerenciador</small>${escapeHtml(item.orgao.nome)}</div>
      <div class="detail-block"><small>Esfera</small>${escapeHtml(displayLabel(item.orgao.esfera))}</div>
      <div class="detail-block"><small>UF</small>${escapeHtml(item.orgao.uf || "Não informada")}</div>
      <div class="detail-block"><small>Início da vigência</small>${escapeHtml(formatDate(item.vigencia_inicio))}</div>
      <div class="detail-block"><small>Fim da vigência</small>${escapeHtml(formatDate(item.vigencia_fim))}</div>
      <div class="detail-block"><small>Situação</small>${escapeHtml(displayLabel(item.situacao))}</div>
      <div class="detail-block"><small>Possibilidade de adesão</small>${item.possibilidade_adesao === true ? "Sim, conforme dado do PNCP" : item.possibilidade_adesao === false ? "Não" : "Não informada"}</div>
    </div>
    <section class="detail-section">
      <h3>Objeto</h3>
      <p>${escapeHtml(item.objeto)}</p>
    </section>
    <section class="detail-section">
      <h3>Identificação PNCP</h3>
      <p>${escapeHtml(item.numero_controle_pncp)}</p>
    </section>
    <section class="detail-section">
      <h3>Itens encontrados</h3>
      ${
        item.itens?.length
          ? item.itens
              .map(
                (entry) => `
                  <div class="registry-item-detail">
                    <strong>Item ${escapeHtml(entry.numero_item)} · ${escapeHtml(displayLabel(entry.disponibilidade))}</strong>
                    <p>${escapeHtml(entry.descricao)}</p>
                    <div class="detail-grid">
                      <div class="detail-block"><small>Registrada</small>${escapeHtml(formatNumber(entry.quantidade_registrada))}</div>
                      <div class="detail-block"><small>Empenhada</small>${escapeHtml(formatNumber(entry.quantidade_empenhada))}</div>
                      <div class="detail-block"><small>Saldo estimado</small>${escapeHtml(formatNumber(entry.saldo_estimado))}</div>
                      <div class="detail-block"><small>Limite de adesão</small>${escapeHtml(formatNumber(entry.limite_adesao))}</div>
                      <div class="detail-block"><small>Valor unitário</small>${escapeHtml(formatCurrency(entry.valor_unitario))}</div>
                      <div class="detail-block"><small>Fornecedor</small>${escapeHtml(entry.fornecedor?.razao_social || "Não informado")}</div>
                    </div>
                  </div>
                `,
              )
              .join("")
          : "<p>Nenhum item armazenado corresponde aos filtros atuais.</p>"
      }
    </section>
  `;
  elements.dialog.showModal();
}

function csvValue(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

async function exportAll() {
  elements.exportCsv.disabled = true;
  elements.status.textContent = "Preparando CSV com todos os resultados filtrados…";
  try {
    const endpoint =
      state.view === "registries" ? "/atas" : "/pncp/oportunidades";
    const first = await apiFetch(`${endpoint}?${queryString(1, 200)}`);
    const items = [...first.items];
    for (let page = 2; page <= first.total_pages; page += 1) {
      const data = await apiFetch(`${endpoint}?${queryString(page, 200)}`);
      items.push(...data.items);
      elements.status.textContent = `Preparando CSV: ${items.length} de ${first.total}…`;
    }
    const opportunityColumns = [
      ["numero_controle_pncp", "Número PNCP"],
      ["orgao_razao_social", "Órgão"],
      ["uf", "UF"],
      ["municipio", "Município"],
      ["data_publicacao_pncp", "Publicação"],
      ["objeto_compra", "Objeto"],
      ["classificacao", "Classificação"],
      ["pontuacao", "Pontuação"],
      ["adequacao_perfil", "Adequação"],
      ["pontuacao_adequacao", "Pontuação de adequação"],
      ["revisao_status", "Revisão"],
      ["perfil_versao", "Perfil"],
      ["analisador_versao", "Analisador"],
      ["link_sistema_origem", "Link"],
    ];
    const registryColumns = [
      ["numero_controle_pncp", "Número PNCP"],
      ["numero_ata", "Número da ata"],
      ["objeto", "Objeto"],
      ["vigencia_inicio", "Início da vigência"],
      ["vigencia_fim", "Fim da vigência"],
      ["situacao", "Situação"],
      ["orgao.nome", "Órgão"],
      ["orgao.cnpj", "CNPJ"],
      ["orgao.esfera", "Esfera"],
      ["orgao.uf", "UF"],
      ["itens.0.numero_item", "Primeiro item"],
      ["itens.0.descricao", "Descrição do primeiro item"],
      ["itens.0.quantidade_registrada", "Quantidade registrada"],
      ["itens.0.quantidade_empenhada", "Quantidade empenhada"],
      ["itens.0.saldo_estimado", "Saldo estimado"],
      ["itens.0.limite_adesao", "Limite de adesão"],
      ["itens.0.valor_unitario", "Valor unitário"],
      ["itens.0.disponibilidade", "Disponibilidade"],
    ];
    const columns =
      state.view === "registries" ? registryColumns : opportunityColumns;
    const valueAt = (item, key) =>
      key.split(".").reduce((value, part) => value?.[part], item);
    const rows = [
      columns.map(([, label]) => csvValue(label)).join(";"),
      ...items.map((item) =>
        columns.map(([key]) => csvValue(valueAt(item, key))).join(";"),
      ),
    ];
    const blob = new Blob([`\ufeff${rows.join("\r\n")}`], {
      type: "text/csv;charset=utf-8",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `sigarp-oportunidades-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    elements.status.textContent = `CSV exportado com ${items.length} registro(s).`;
  } catch (error) {
    elements.status.textContent = error.message;
  } finally {
    elements.exportCsv.disabled = false;
  }
}

elements.accessForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.accessError.textContent = "";
  try {
    await connect(elements.token.value);
  } catch (error) {
    elements.accessError.textContent = error.message;
  }
});

elements.changeToken.addEventListener("click", () => {
  sessionStorage.removeItem("sigarp_token");
  state.token = "";
  showAccess();
});

elements.filters.addEventListener("submit", (event) => {
  event.preventDefault();
  state.filters = collectFilters();
  delete state.filters.consulta;
  state.page = 1;
  loadOpportunities();
});

function configureView() {
  state.view = elements.consultationView.value;
  document.querySelectorAll("[data-scope]").forEach((element) => {
    const visible = element.dataset.scope === state.view;
    element.classList.toggle("hidden", !visible);
    element.querySelectorAll("input, select").forEach((control) => {
      control.disabled = !visible;
    });
  });
  if (state.view === "registries") {
    const validOn = elements.filters.elements.namedItem("vigente_em");
    if (!validOn.value) validOn.value = new Date().toISOString().slice(0, 10);
  }
  state.filters = collectFilters();
  delete state.filters.consulta;
  state.page = 1;
  loadOpportunities();
}

elements.consultationView.addEventListener("change", configureView);

elements.clearFilters.addEventListener("click", () => {
  elements.filters.reset();
  elements.consultationView.value = state.view;
  state.filters = collectFilters();
  delete state.filters.consulta;
  state.page = 1;
  loadOpportunities();
});

elements.previousPage.addEventListener("click", () => {
  state.page -= 1;
  loadOpportunities();
});

elements.nextPage.addEventListener("click", () => {
  state.page += 1;
  loadOpportunities();
});

elements.cards.addEventListener("click", (event) => {
  const registryButton = event.target.closest("[data-registry-id]");
  if (registryButton) {
    const item = state.pageData.items.find(
      (entry) => entry.id === Number(registryButton.dataset.registryId),
    );
    if (item) openRegistryDetails(item);
    return;
  }
  const button = event.target.closest("[data-assessment-id]");
  if (!button) return;
  const item = state.pageData.items.find(
    (entry) => entry.assessment_id === Number(button.dataset.assessmentId),
  );
  if (item) openDetails(item);
});

elements.closeDetails.addEventListener("click", () => elements.dialog.close());
elements.exportCsv.addEventListener("click", exportAll);

state.filters = collectFilters();
delete state.filters.consulta;
document.querySelectorAll("[data-scope].hidden input, [data-scope].hidden select").forEach(
  (control) => {
    control.disabled = true;
  },
);
if (state.token) {
  connect(state.token).catch(() => {
    sessionStorage.removeItem("sigarp_token");
    showAccess();
  });
} else {
  showAccess();
}
