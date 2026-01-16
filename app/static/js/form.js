(function () {
  const botsContainer = document.getElementById('botsContainer');
  const addBotBtn = document.getElementById('addBotBtn');
  const template = document.getElementById('botRowTemplate');

  const owedToggle = document.getElementById('owedTicketsToggle');
  const owedAmountWrap = document.getElementById('owedTicketsAmount');
  const owedAmountInput = document.getElementById('fortibots_ticket_amount');

  function getExistingMaxIndex() {
    const rows = botsContainer ? botsContainer.querySelectorAll('.bot-row') : [];
    let max = -1;
    rows.forEach((row) => {
      const idx = parseInt(row.getAttribute('data-index'), 10);
      if (!Number.isNaN(idx)) max = Math.max(max, idx);
    });
    return max;
  }

  let nextIndex = botsContainer ? (getExistingMaxIndex() + 1) : 0;

  function updateTicketVisibility() {
    if (!owedToggle || !owedAmountWrap || !owedAmountInput) return;
    const on = !!owedToggle.checked;
    owedAmountWrap.style.display = on ? '' : 'none';
    if (on) {
      owedAmountInput.setAttribute('required', 'required');
    } else {
      owedAmountInput.removeAttribute('required');
      owedAmountInput.value = '';
    }
  }

  function wireBotRow(rowEl) {
    const removeBtn = rowEl.querySelector('.remove-bot');
    const nameInput = rowEl.querySelector('input[name$="-bot_name"]');
    const amtInput = rowEl.querySelector('input[name$="-subsidy_amount"]');

    if (removeBtn) {
      removeBtn.addEventListener('click', () => {
        // keep at least one row
        const rows = botsContainer.querySelectorAll('.bot-row');
        if (rows.length <= 1) return;
        rowEl.remove();
      });
    }

    // Light client-side guidance: if name is filled, require amount and vice versa
    const syncRequired = () => {
      const hasName = !!(nameInput && nameInput.value.trim());
      const hasAmt = !!(amtInput && amtInput.value.trim());

      if (amtInput) {
        if (hasName) amtInput.setAttribute('required', 'required');
        else amtInput.removeAttribute('required');
      }
      if (nameInput) {
        if (hasAmt) nameInput.setAttribute('required', 'required');
        else nameInput.removeAttribute('required');
      }
    };

    if (nameInput) nameInput.addEventListener('input', syncRequired);
    if (amtInput) amtInput.addEventListener('input', syncRequired);

    syncRequired();
  }

  function addBotRow() {
    if (!botsContainer || !template) return;

    const max = parseInt(botsContainer.getAttribute('data-max') || '100', 10);
    const currentRows = botsContainer.querySelectorAll('.bot-row').length;
    if (currentRows >= max) {
      alert(`Max of ${max} bots reached.`);
      return;
    }

    const html = template.innerHTML.replaceAll('__INDEX__', String(nextIndex));
    nextIndex += 1;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const rowEl = wrapper.firstElementChild;
    if (!rowEl) return;

    botsContainer.appendChild(rowEl);
    wireBotRow(rowEl);
  }

  // Init
  if (botsContainer) {
    botsContainer.querySelectorAll('.bot-row').forEach(wireBotRow);
  }

  if (addBotBtn) {
    addBotBtn.addEventListener('click', addBotRow);
  }

  if (owedToggle) {
    owedToggle.addEventListener('change', updateTicketVisibility);
  }

  // initial state
  if (typeof window.__INITIAL_TICKETS_CHECKED__ !== 'undefined') {
    if (owedToggle) owedToggle.checked = !!window.__INITIAL_TICKETS_CHECKED__;
  }
  updateTicketVisibility();
})();
