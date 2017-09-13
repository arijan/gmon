Number.prototype.pad = function(size) {
  var s = String(this);

  while (s.length < (size || 2)) { s = "0" + s; }

  return s; }

getColRows = function(node) {
  var tab = node.parentElement.parentElement.parentElement.parentElement.parentElement;

  return { col: Number(node.getAttribute('column')), rows: tab.children[0].children, tab: tab }; }

hideThisColumn = function(node) {
  var colrows = getColRows(node);
  var col = colrows.col;
  var rows = colrows.rows;

  for (var i=0; i < rows.length; i++) { rows[i].children[col].hidden=true; } }

unhideAllColumns = function(node) {
  var colrows = getColRows(node);
  var col = colrows.col;
  var rows = colrows.rows;
  var refresh = false, allfilters;

  for (var i=0; i < rows.length; i++) {
    rows[i].hidden = false;

    for (var j=0; j < rows[i].children.length; j++) {
        rows[i].children[j].hidden=false; } }

  for (i = 0; i < sessionStorage.length; i++) {
    key = sessionStorage.key(i)
    keysplit = key.split(':');

    if (keysplit[1] === 'filter') {
      sessionStorage.removeItem(key);
      allfilters = document.getElementById(keysplit[0]).getElementsByClassName('tablefilter');

      for (j = 0; j < allfilters.length; j++) {
        allfilters[j].value = ''; }

      refresh = true; } }

  if (refresh) {
    filteratstart(); } }

sortByColumn = function(node) {
  var arr = new Array();
  var i, j, cells, clen, pad, percent = false;
  var colrows = getColRows(node);
  var col = colrows.col;
  var rows = colrows.rows;
  var rlen = rows.length;

  if (rows[rlen-1].children[1].innerHTML === "") {
    rlen -= 1; }

  if (node.innerHTML === "↓" || node.innerHTML === "⇵") {
    var asc = 1;
    var negasc = -1;
    node.innerHTML = "↑"; }
  else {
    var asc = -1;
    var negasc = 1;
    node.innerHTML = "↓"; }

  var attrib = colrows.tab.getAttribute('id');

  if (attrib) {
    sessionStorage.setItem(attrib + ':sort', col * (node.innerHTML === "↑" ? 1 : -1)); }

  for (j = 0, cells = rows[0].getElementsByTagName("button"); j < cells.length; j++) {
    if ((cells[j].innerHTML === "↓" || cells[j].innerHTML === "↑" ) && cells[j] !== node) {
      cells[j].innerHTML = "⇵"; } }

  for (i = 1; i < rlen; i++) {
    cells = rows[i].children;
    clen = cells.length;
    arr[i-1] = new Array();
    for (j = 0; j < clen; j++) { arr[i-1][j] = cells[j].innerHTML; }
    pad = asc === 1 ? i.pad(6) : (1000000-i).pad(6);
    j = arr[i-1][col];
    if  (j[j.length - 1] === '%') { j = Number(j.slice(0, -1)); percent = true; }
    arr[i-1][col] = j + pad; }

  arr.sort(function(a, b) { ca = a[col];
                            cb = b[col];

                            if (isNaN(ca) || isNaN(cb)) {
                                return ca.localeCompare(cb) === 1 ? asc : (-1 * asc); }
                            else {
                                return Number(ca) < Number(cb) ? asc : (-1 * asc); } });

  for (i = 0; i < arr.length; i++) {
    arr[i][col] = arr[i][col].slice(0,-6);

    if (percent) {
       if (arr[i][col] !== '') {
         arr[i][col] += ' %'; } } }

  for (var rowidx = 1; rowidx < rlen; rowidx++) {
    for (var colidx = 1; colidx < clen; colidx++) { rows[rowidx].cells[colidx].innerHTML = arr[rowidx-1][colidx]; } }

  filteratstart(); }

function filterByColumn(node) {
  var colrows = getColRows(node);
  var col = colrows.col;
  var rows = colrows.rows;
  var filter, i, j, all;
  var allfilters = colrows.tab.getElementsByClassName('tablefilter');

  var attrib = colrows.tab.getAttribute('id');

  if (attrib) {
    if (node.value !== '') {
      sessionStorage.setItem(attrib + ':filter', String(col) + ':' + node.value.toLowerCase()); }
    else {
      sessionStorage.removeItem(attrib + ':filter'); } }

  for (i = 1; i < rows.length - (rows[rows.length - 1].children[1].innerHTML === "" ? 1 : 0); i++) {
    all = true;

    for (j = 0; j < allfilters.length; j++) {
      filter = allfilters[j].value.toLowerCase();
      col = Number(allfilters[j].attributes.column.value);

      if (filter.length > 0) {
        if (!rows[i].children[col].innerHTML.toLowerCase().includes(filter)) {
          all = false; } }

      if (all) {
          rows[i].hidden = false; }
      else {
          rows[i].hidden = true; } } } }

function sortatstart() {
	var i, j, val, key, obj;

	for (i = 0; i < sessionStorage.length; i++) {
        key = sessionStorage.key(i);
        val = sessionStorage.getItem(key);

        key = key.split(':')
        id = key[0];

        if (key[1] === 'sort') {
          obj = document.getElementById(id);

          if (obj) {
            obj = obj.children[0].children[0].children[Math.abs(val)].children[0].children[1];

            for (j = 0; j < (val < 0 ? 2: 1); j++)
		      sortByColumn(obj); } } } }

function filteratstart() {
	var i, j, val, key, obj;

	for (i = 0; i < sessionStorage.length; i++) {
        key = sessionStorage.key(i);
        val = sessionStorage.getItem(key);

        key = key.split(':')
        id = key[0];

        if (key[1] === 'filter') {
          val = val.split(':');
          col = val[0];
          filter = val[1];

          if (filter !== '') {
            allfilters = document.getElementById(id);

            if (allfilters) {
              allfilters = allfilters.getElementsByClassName('tablefilter');

              for (j = 0; j < allfilters.length; j++) {
                if (allfilters[j].attributes.column.value === col) {
                  allfilters[j].value = filter;
                  filterByColumn(allfilters[j]); } } } } } } }

window.addEventListener("load", function() {
  sortatstart();
  filteratstart(); });