// Reports JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeTableSorting();
    initializeFilterHandling();
  });
  
  // Table sorting functionality
  function initializeTableSorting() {
    const table = document.getElementById('recordsTable');
    if (!table) return;
  
    const headers = table.querySelectorAll('th.sortable');
    
    headers.forEach(header => {
      header.addEventListener('click', function() {
        const column = this.dataset.column;
        const currentSort = this.classList.contains('sort-asc') ? 'asc' : 
                           this.classList.contains('sort-desc') ? 'desc' : 'none';
        
        // Remove sort classes from all headers
        headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
        
        // Determine new sort direction
        let newSort;
        if (currentSort === 'none' || currentSort === 'desc') {
          newSort = 'asc';
          this.classList.add('sort-asc');
        } else {
          newSort = 'desc';
          this.classList.add('sort-desc');
        }
        
        sortTable(table, column, newSort);
      });
    });
  }
  
  function sortTable(table, column, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.no-records)'));
    
    rows.sort((a, b) => {
      let aVal = getCellValue(a, column);
      let bVal = getCellValue(b, column);
      
      // Handle different data types
      if (!isNaN(aVal) && !isNaN(bVal)) {
        aVal = parseFloat(aVal);
        bVal = parseFloat(bVal);
      } else if (isDate(aVal) && isDate(bVal)) {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      } else {
        aVal = aVal.toString().toLowerCase();
        bVal = bVal.toString().toLowerCase();
      }
      
      if (direction === 'asc') {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
      }
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
  }
  
  function getCellValue(row, column) {
    const columnMap = {
      'name': 0,
      'date': 1,
      'vehicle_no': 2,
      'source_panchayat': 3,
      'waste_type': 4,
      'weight_kg': 5,
      'created': 7
    };
    
    const cellIndex = columnMap[column];
    const cell = row.cells[cellIndex];
    return cell ? cell.textContent.trim() : '';
  }
  
  function isDate(value) {
    return !isNaN(Date.parse(value));
  }
  
  // Filter handling
  function initializeFilterHandling() {
    const filterForm = document.getElementById('recordsFilter');
    if (!filterForm) return;
  
    // Add loading state to filter form
    filterForm.addEventListener('submit', function() {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Applying Filters...';
        
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Apply Filters';
        }, 2000);
      }
    });
  }
  
  function clearFilters() {
    const form = document.getElementById('recordsFilter');
    if (!form) return;
    
    // Clear all form inputs
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
      if (input.type === 'checkbox' || input.type === 'radio') {
        input.checked = false;
      } else {
        input.value = '';
      }
    });
    
    // Submit the form to refresh with no filters
    form.submit();
  }
  
  // Print functionality
  function printReport() {
    // Hide non-printable sections
    const nonPrintable = document.querySelectorAll('.filters-section, .export-section');
    nonPrintable.forEach(section => {
      section.style.display = 'none';
    });
    
    // Print the page
    window.print();
    
    // Restore hidden sections
    nonPrintable.forEach(section => {
      section.style.display = 'block';
    });
  }
  
  // Export functionality helpers
  function exportTableToCSV() {
    const table = document.getElementById('recordsTable');
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
      const cells = row.querySelectorAll('th, td');
      const rowData = Array.from(cells).map(cell => {
        let text = cell.textContent.trim();
        // Escape quotes and wrap in quotes if contains comma
        if (text.includes(',') || text.includes('"')) {
          text = '"' + text.replace(/"/g, '""') + '"';
        }
        return text;
      });
      csv.push(rowData.join(','));
    });
    
    // Create and download CSV file
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `waste_records_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
  
  // Add keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Ctrl+P for print
    if (e.ctrlKey && e.key === 'p') {
      e.preventDefault();
      printReport();
    }
    
    // Ctrl+E for export (focus on first export button)
    if (e.ctrlKey && e.key === 'e') {
      e.preventDefault();
      const firstExportBtn = document.querySelector('.btn-export');
      if (firstExportBtn) {
        firstExportBtn.focus();
      }
    }
  });
  
  // Add tooltips for better UX
  function addTooltips() {
    const tooltipElements = [
      { selector: '.btn-csv', text: 'Export data as CSV file' },
      { selector: '.btn-pdf', text: 'Export data as PDF file' },
      { selector: '.btn-print', text: 'Print this report (Ctrl+P)' },
      { selector: '.sortable', text: 'Click to sort by this column' }
    ];
    
    tooltipElements.forEach(({ selector, text }) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.title = text;
      });
    });
  }
  
  // Initialize tooltips when DOM is loaded
  document.addEventListener('DOMContentLoaded', addTooltips);
  