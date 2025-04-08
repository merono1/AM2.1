document.addEventListener("DOMContentLoaded", function() {
    // Habilitar/deshabilitar controles de filtros avanzados
    document.getElementById("filterFechaCheck").addEventListener("change", function() {
        document.getElementById("filterFechaDesde").disabled = !this.checked;
        document.getElementById("filterFechaHasta").disabled = !this.checked;
    });
    document.getElementById("filterTecnicoCheck").addEventListener("change", function() {
        document.getElementById("filterTecnico").disabled = !this.checked;
    });
    document.getElementById("filterTipoCheck").addEventListener("change", function() {
        document.getElementById("filterTipo").disabled = !this.checked;
    });
    document.getElementById("filterEstadoCheck").addEventListener("change", function() {
        document.getElementById("filterEstado").disabled = !this.checked;
    });
    document.getElementById("filterClienteCheck").addEventListener("change", function() {
        document.getElementById("filterCliente").disabled = !this.checked;
    });
    document.getElementById("filterAprobacionCheck").addEventListener("change", function() {
        document.getElementById("filterAprobacion").disabled = !this.checked;
    });

    function applyAllFilters() {
        var filterFechaActive = document.getElementById("filterFechaCheck").checked;
        var fechaDesde = document.getElementById("filterFechaDesde").value;
        var fechaHasta = document.getElementById("filterFechaHasta").value;
        var filterTecnico = document.getElementById("filterTecnico").value.toLowerCase();
        var filterTipo = document.getElementById("filterTipo").value.toLowerCase();
        var filterEstado = document.getElementById("filterEstado").value.toLowerCase();
        var filterAprobacion = document.getElementById("filterAprobacion").value.toLowerCase();
        var filterCliente = document.getElementById("filterCliente").value.toLowerCase();
        var searchValue = document.getElementById("searchInput").value.toLowerCase();

        var rows = document.querySelectorAll("#presupuestosTable tbody tr");
        rows.forEach(function(row) {
            var showRow = true;
            // Búsqueda simple en celdas 0 a 5 (ID, Referencia, Fecha, Cliente, Tipo Proyecto, Nombre Proyecto)
            var cellText = "";
            for (var i = 0; i <= 5; i++) {
                if (row.cells[i]) {
                    cellText += row.cells[i].innerText.toLowerCase() + " ";
                }
            }
            if (searchValue && cellText.indexOf(searchValue) === -1) {
                showRow = false;
            }
            // Filtro por fecha (columna 2)
            if (filterFechaActive && row.cells[2]) {
                var fechaText = row.cells[2].innerText.trim();
                if (fechaText) {
                    var rowDate = new Date(fechaText);
                    if (!isNaN(rowDate)) {
                        if (fechaDesde && rowDate < new Date(fechaDesde)) {
                            showRow = false;
                        }
                        if (fechaHasta && rowDate > new Date(fechaHasta)) {
                            showRow = false;
                        }
                    }
                }
            }
            // Filtro por técnico (columna 6)
            if (filterTecnico && row.cells[6]) {
                var tecnicoSelect = row.cells[6].querySelector("select");
                var tecnicoVal = tecnicoSelect ? tecnicoSelect.value.toLowerCase() : "";
                if (tecnicoVal.indexOf(filterTecnico) === -1) {
                    showRow = false;
                }
            }
            // Filtro por tipo de proyecto (columna 4)
            if (filterTipo && row.cells[4]) {
                var tipoVal = row.cells[4].innerText.trim().toLowerCase();
                if (tipoVal.indexOf(filterTipo) === -1) {
                    showRow = false;
                }
            }
            // Filtro por estado (columna 9)
            if (filterEstado && row.cells[9]) {
                var estadoSelect = row.cells[9].querySelector("select");
                var estadoVal = estadoSelect ? estadoSelect.value.toLowerCase() : "";
                if (estadoVal.indexOf(filterEstado) === -1) {
                    showRow = false;
                }
            }
            // Filtro por aprobación (columna 7)
            if (filterAprobacion && row.cells[7]) {
                var aprobacionRadio = row.cells[7].querySelector("input.estado-radio:checked");
                var aprobacionVal = aprobacionRadio ? aprobacionRadio.value.toLowerCase() : "";
                if (aprobacionVal.indexOf(filterAprobacion) === -1) {
                    showRow = false;
                }
            }
            // Filtro por cliente (columna 3)
            if (filterCliente && row.cells[3]) {
                var clienteVal = row.cells[3].innerText.trim().toLowerCase();
                if (clienteVal.indexOf(filterCliente) === -1) {
                    showRow = false;
                }
            }
            row.style.display = showRow ? "" : "none";
        });
    }
    document.getElementById("applyFilters").addEventListener("click", applyAllFilters);
    document.getElementById("searchInput").addEventListener("keyup", applyAllFilters);

    // Modal y botones de acciones
    var hojaModal = new bootstrap.Modal(document.getElementById('hojaModal'));
    document.querySelectorAll(".hoja-btn").forEach(function(button) {
        button.addEventListener("click", function() {
            var presupuestoId = this.getAttribute("data-presupuesto-id");
            var generarForm = document.getElementById("generarNuevoForm");
            generarForm.action = "/hojas_trabajo/clonar/" + presupuestoId;
            hojaModal.show();
        });
    });
    document.querySelectorAll(".modificar-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            var row = this.closest("tr");
            var id = row.getAttribute("data-id");
            console.log("Editar presupuesto con id:", id);
            window.location.href = "{{ url_for('presupuestos_bp.editar_presupuesto', id=0) }}".replace("0", id);
        });
    });
    function guardarCambios(row) {
        var id = row.getAttribute("data-id");
        var tecnico = row.querySelector(".tecnico-select").value;
        var estadoRadio = row.querySelector("input.estado-radio:checked");
        var aprobacion = estadoRadio ? estadoRadio.value : "";
        var fecha_aprobacion = row.querySelector(".fecha-aprobacion").value;
        var estado = row.querySelector(".estado-select").value;
        var formData = new FormData();
        formData.append("tecnico", tecnico);
        formData.append("aprobacion", aprobacion);
        formData.append("fecha_aprobacion", fecha_aprobacion);
        formData.append("estado", estado);
        fetch("{{ url_for('presupuestos_bp.actualizar_presupuesto_estado', id=0) }}".replace("0", id), {
            method: "POST",
            body: formData
        }).then(response => response.text())
          .then(data => {
              console.log("Cambios guardados para el presupuesto " + id);
          }).catch(error => {
              console.error("Error al guardar los cambios", error);
          });
    }
    document.querySelectorAll("input.estado-radio").forEach(function(radio) {
        radio.addEventListener("change", function() {
            var row = this.closest("tr");
            var fechaInput = row.querySelector(".fecha-aprobacion");
            var today = new Date();
            var yyyy = today.getFullYear();
            var mm = String(today.getMonth() + 1).padStart(2, "0");
            var dd = String(today.getDate()).padStart(2, "0");
            var todayStr = yyyy + "-" + mm + "-" + dd;
            if (this.value === "aceptado" || this.value === "rechazado") {
                fechaInput.value = todayStr;
            }
            row.classList.remove("table-success", "table-danger");
            if (this.value === "aceptado") {
                row.classList.add("table-success");
            } else if (this.value === "rechazado") {
                row.classList.add("table-danger");
            }
            guardarCambios(row);
        });
    });
    document.querySelectorAll(".guardar-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            var row = this.closest("tr");
            guardarCambios(row);
        });
    });
});
