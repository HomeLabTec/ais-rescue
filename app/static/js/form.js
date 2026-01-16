(function () {
  const botsContainer = document.getElementById('botsContainer');
  const addBotBtn = document.getElementById('addBotBtn');
  const template = document.getElementById('botRowTemplate');

  const owedToggle = document.getElementById('owedTicketsToggle');
  const owedAmountWrap = document.getElementById('owedTicketsAmount');
  const owedAmountInput = document.getElementById('fortibots_ticket_amount');

  const owedYyToggle = document.getElementById('owedYyBotsToggle');
  const yyBotsWrap = document.getElementById('owedYyBotsDetails');
  const yyBotsContainer = document.getElementById('yyBotsContainer');
  const addYyBotBtn = document.getElementById('addYyBotBtn');
  const yyBotTemplate = document.getElementById('yyBotRowTemplate');

  const pendingWithdrawsToggle = document.getElementById('pendingWithdrawsToggle');
  const pendingWithdrawsWrap = document.getElementById('pendingWithdrawsDetails');
  const withdrawDatesContainer = document.getElementById('withdrawDatesContainer');
  const addWithdrawDateBtn = document.getElementById('addWithdrawDateBtn');
  const withdrawDateTemplate = document.getElementById('withdrawDateRowTemplate');

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
  let nextYyIndex = 0;
  let nextWithdrawIndex = 0;

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

  function getExistingYyMaxIndex() {
    const rows = yyBotsContainer ? yyBotsContainer.querySelectorAll('.yy-bot-row') : [];
    let max = -1;
    rows.forEach((row) => {
      const idx = parseInt(row.getAttribute('data-index'), 10);
      if (!Number.isNaN(idx)) max = Math.max(max, idx);
    });
    return max;
  }

  function updateYyVisibility() {
    if (!owedYyToggle || !yyBotsWrap || !yyBotsContainer) return;
    const on = !!owedYyToggle.checked;
    yyBotsWrap.style.display = on ? '' : 'none';

    if (on && yyBotsContainer.querySelectorAll('.yy-bot-row').length === 0) {
      addYyBotRow();
    }

    const inputs = yyBotsContainer.querySelectorAll('input[name^="yy_bots-"]');
    inputs.forEach((input, idx) => {
      if (on && idx === 0) {
        input.setAttribute('required', 'required');
      } else {
        input.removeAttribute('required');
        if (!on) input.value = '';
      }
    });
  }

  function getExistingWithdrawMaxIndex() {
    const rows = withdrawDatesContainer ? withdrawDatesContainer.querySelectorAll('.withdraw-date-row') : [];
    let max = -1;
    rows.forEach((row) => {
      const idx = parseInt(row.getAttribute('data-index'), 10);
      if (!Number.isNaN(idx)) max = Math.max(max, idx);
    });
    return max;
  }

  function addWithdrawDateRow() {
    if (!withdrawDatesContainer || !withdrawDateTemplate) return;

    const max = parseInt(withdrawDatesContainer.getAttribute('data-max') || '2', 10);
    const currentRows = withdrawDatesContainer.querySelectorAll('.withdraw-date-row').length;
    if (currentRows >= max) {
      alert(`Max of ${max} withdraw dates reached.`);
      return;
    }

    const html = withdrawDateTemplate.innerHTML.replaceAll('__INDEX__', String(nextWithdrawIndex));
    nextWithdrawIndex += 1;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const rowEl = wrapper.firstElementChild;
    if (!rowEl) return;

    withdrawDatesContainer.appendChild(rowEl);
  }

  function updateWithdrawVisibility() {
    if (!pendingWithdrawsToggle || !pendingWithdrawsWrap || !withdrawDatesContainer) return;
    const on = !!pendingWithdrawsToggle.checked;
    pendingWithdrawsWrap.style.display = on ? '' : 'none';

    if (on && withdrawDatesContainer.querySelectorAll('.withdraw-date-row').length === 0) {
      addWithdrawDateRow();
    }

    const inputs = withdrawDatesContainer.querySelectorAll('input[name^="withdraw_dates-"]');
    inputs.forEach((input, idx) => {
      if (on && idx === 0) {
        input.setAttribute('required', 'required');
      } else {
        input.removeAttribute('required');
        if (!on) input.value = '';
      }
    });
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

  function addYyBotRow() {
    if (!yyBotsContainer || !yyBotTemplate) return;

    const max = parseInt(yyBotsContainer.getAttribute('data-max') || '14', 10);
    const currentRows = yyBotsContainer.querySelectorAll('.yy-bot-row').length;
    if (currentRows >= max) {
      alert(`Max of ${max} YY bots reached.`);
      return;
    }

    const html = yyBotTemplate.innerHTML.replaceAll('__INDEX__', String(nextYyIndex));
    nextYyIndex += 1;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const rowEl = wrapper.firstElementChild;
    if (!rowEl) return;

    yyBotsContainer.appendChild(rowEl);
  }

  // Init
  if (botsContainer) {
    botsContainer.querySelectorAll('.bot-row').forEach(wireBotRow);
  }

  if (addBotBtn) {
    addBotBtn.addEventListener('click', addBotRow);
  }

  if (yyBotsContainer) {
    nextYyIndex = getExistingYyMaxIndex() + 1;
  }

  if (addYyBotBtn) {
    addYyBotBtn.addEventListener('click', addYyBotRow);
  }

  if (withdrawDatesContainer) {
    nextWithdrawIndex = getExistingWithdrawMaxIndex() + 1;
  }

  if (addWithdrawDateBtn) {
    addWithdrawDateBtn.addEventListener('click', addWithdrawDateRow);
  }

  if (owedToggle) {
    owedToggle.addEventListener('change', updateTicketVisibility);
  }

  if (owedYyToggle) {
    owedYyToggle.addEventListener('change', updateYyVisibility);
  }

  if (pendingWithdrawsToggle) {
    pendingWithdrawsToggle.addEventListener('change', updateWithdrawVisibility);
  }

  // initial state
  if (typeof window.__INITIAL_TICKETS_CHECKED__ !== 'undefined') {
    if (owedToggle) owedToggle.checked = !!window.__INITIAL_TICKETS_CHECKED__;
  }
  if (typeof window.__INITIAL_YY_BOTS_CHECKED__ !== 'undefined') {
    if (owedYyToggle) owedYyToggle.checked = !!window.__INITIAL_YY_BOTS_CHECKED__;
  }
  if (typeof window.__INITIAL_PENDING_WITHDRAWS_CHECKED__ !== 'undefined') {
    if (pendingWithdrawsToggle) pendingWithdrawsToggle.checked = !!window.__INITIAL_PENDING_WITHDRAWS_CHECKED__;
  }
  updateTicketVisibility();
  updateYyVisibility();
  updateWithdrawVisibility();
})();
