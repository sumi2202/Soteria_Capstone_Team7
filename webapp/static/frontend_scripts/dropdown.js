document.addEventListener('DOMContentLoaded', () => {
  const dropdown = document.getElementById('dropdown');
  const selected = document.getElementById('selected');
  const optionsContainer = document.getElementById('options');
  const hiddenInput = document.getElementById('sql_level_risk');
  const sqlLabelInput = document.getElementById('sql_label');

  selected.addEventListener('click', () => {
    optionsContainer.classList.toggle('show');
  });

  document.querySelectorAll('.options li').forEach(option => {
    option.addEventListener('click', () => {
      selected.textContent = option.textContent;
      hiddenInput.value = option.getAttribute('data-value');
      sqlLabelInput.value = option.textContent.split(' - ')[0].trim();
      optionsContainer.classList.remove('show');
    });
  });

  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) {
      optionsContainer.classList.remove('show');
    }
  });
});
