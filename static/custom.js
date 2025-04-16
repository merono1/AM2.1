document.addEventListener("DOMContentLoaded", function() {
    // Función auxiliar: asigna listener si el elemento existe
    function onElement(id, event, callback) {
        var el = document.getElementById(id);
        if (el) {
            el.addEventListener(event, callback);
        }
    }

    // Asignar eventos a controles de filtros (si existen)
    onElement("filterFechaCheck", "change", function() {
        var desde = document.getElementById("filterFechaDesde");
        var hasta = document.getElementById("filterFechaHasta");
        if (desde && hasta) {
            desde.disabled = !this.checked;
            hasta.disabled = !this.checked;
        }
    });
    onElement("filterTecnicoCheck", "change", function() {
        var el = document.getElementById("filterTecnico");
        if (el) el.disabled = !this.checked;
    });
    onElement("filterTipoCheck", "change", function() {
        var el = document.getElementById("filterTipo");
        if (el) el.disabled = !this.checked;
    });
    onElement("filterEstadoCheck", "change", function() {
        var el = document.getElementById("filterEstado");
        if (el) el.disabled = !this.checked;
    });
    onElement("filterClienteCheck", "change", function() {
        var el = document.getElementById("filterCliente");
        if (el) el.disabled = !this.checked;
    });
    onElement("filterAprobacionCheck", "change", function() {
        var el = document.getElementById("filterAprobacion");
        if (el) el.disabled = !this.checked;
    });

    // Función para aplicar filtros avanzados y búsqueda simple
    function applyAllFilters() {
        var filterFechaActive = document.getElementById("filterFechaCheck") ? document.getElementById("filterFechaCheck").checked : false;
        var fechaDesde = document.getElementById("filterFechaDesde") ? document.getElementById("filterFechaDesde").value : "";
        var fechaHasta = document.getElementById("filterFechaHasta") ? document.getElementById("filterFechaHasta").value : "";
        var filterTecnico = document.getElementById("filterTecnico") ? document.getElementById("filterTecnico").value.toLowerCase() : "";
        var filterTipo = document.getElementById("filterTipo") ? document.getElementById("filterTipo").value.toLowerCase() : "";
        var filterEstado = document.getElementById("filterEstado") ? document.getElementById("filterEstado").value.toLowerCase() : "";
        var filterAprobacion = document.getElementById("filterAprobacion") ? document.getElementById("filterAprobacion").value.toLowerCase() : "";
        var filterCliente = document.getElementById("filterCliente") ? document.getElementById("filterCliente").value.toLowerCase() : "";
        var searchValue = document.getElementById("searchInput") ? document.getElementById("searchInput").value.toLowerCase() : "";

        var rows = document.querySelectorAll("#presupuestosTable tbody tr");
        rows.forEach(function(row) {
            var showRow = true;
            var cellText = "";
            for (var i = 0; i <= 5; i++) {
                if (row.cells[i]) {
                    cellText += row.cells[i].innerText.toLowerCase() + " ";
                }
            }
            if (searchValue && cellText.indexOf(searchValue) === -1) {
                showRow = false;
            }
            if (filterFechaActive && row.cells[2]) {
                var fechaText = row.cells[2].innerText.trim();
                if (fechaText) {
                    var rowDate = new Date(fechaText);
                    if (!isNaN(rowDate)) {
                        if (fechaDesde && rowDate < new Date(fechaDesde)) showRow = false;
                        if (fechaHasta && rowDate > new Date(fechaHasta)) showRow = false;
                    }
                }
            }
            if (filterTecnico && row.cells[6]) {
                var tecnicoSelect = row.cells[6].querySelector("select");
                var tecnicoVal = tecnicoSelect ? tecnicoSelect.value.toLowerCase() : "";
                if (tecnicoVal.indexOf(filterTecnico) === -1) showRow = false;
            }
            if (filterTipo && row.cells[4]) {
                var tipoVal = row.cells[4].innerText.trim().toLowerCase();
                if (tipoVal.indexOf(filterTipo) === -1) showRow = false;
            }
            if (filterEstado && row.cells[9]) {
                var estadoSelect = row.cells[9].querySelector("select");
                var estadoVal = estadoSelect ? estadoSelect.value.toLowerCase() : "";
                if (estadoVal.indexOf(filterEstado) === -1) showRow = false;
            }
            if (filterAprobacion && row.cells[7]) {
                var aprobacionRadio = row.cells[7].querySelector("input.estado-radio:checked");
                var aprobacionVal = aprobacionRadio ? aprobacionRadio.value.toLowerCase() : "";
                if (aprobacionVal.indexOf(filterAprobacion) === -1) showRow = false;
            }
            if (filterCliente && row.cells[3]) {
                var clienteVal = row.cells[3].innerText.trim().toLowerCase();
                if (clienteVal.indexOf(filterCliente) === -1) showRow = false;
            }
            row.style.display = showRow ? "" : "none";
        });
    }
    var applyFiltersBtn = document.getElementById("applyFilters");
    if (applyFiltersBtn) applyFiltersBtn.addEventListener("click", applyAllFilters);
    var searchInput = document.getElementById("searchInput");
    if (searchInput) searchInput.addEventListener("keyup", applyAllFilters);

    // Manejo de modal "H.Trabajo"
    var hojaModalEl = document.getElementById("hojaModal");
    if (hojaModalEl) {
        var hojaModal = new bootstrap.Modal(hojaModalEl);
        document.querySelectorAll(".hoja-btn").forEach(function(button) {
            button.addEventListener("click", function() {
                var presupuestoId = this.getAttribute("data-presupuesto-id");
                var generarForm = document.getElementById("generarNuevoForm");
                if (generarForm) {
                    generarForm.action = "/hojas_trabajo/clonar/" + presupuestoId;
                }
                hojaModal.show();
            });
        });
    }

    // Botón de editar en la tabla de presupuestos
    document.querySelectorAll(".modificar-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            var row = this.closest("tr");
            var id = row.getAttribute("data-id");
            window.location.href = "/presupuestos/editar/" + id;
        });
    });

    // Función para guardar cambios vía AJAX
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
        fetch("/presupuestos/actualizar/" + id, {
            method: "POST",
            body: formData
        }).then(response => response.text())
          .then(data => console.log("Cambios guardados para el presupuesto " + id))
          .catch(error => console.error("Error al guardar los cambios", error));
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
            if (this.value === "aceptado") row.classList.add("table-success");
            else if (this.value === "rechazado") row.classList.add("table-danger");
            guardarCambios(row);
        });
    });
    document.querySelectorAll(".guardar-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            var row = this.closest("tr");
            guardarCambios(row);
        });
    });

    // Funcionalidad centralizada para copiar al portapapeles
    document.querySelectorAll(".copiar-btn").forEach(function(boton) {
        boton.addEventListener("click", function() {
            var valor = this.getAttribute("data-correo") || this.getAttribute("data-valor") || "";
            navigator.clipboard.writeText(valor).then(function() {
                var originalText = "Copiar";
                boton.textContent = "Copiado";
                setTimeout(function() {
                    boton.textContent = originalText;
                }, 1500);
            }).catch(function(error) {
                console.error("Error copiando al portapapeles", error);
            });
        });
    });

    // Optimización: Event Delegation para elementos dinámicos en el contenedor de capítulos
    var capitulosContainer = document.getElementById("capitulosContainer");
    if (capitulosContainer) {
        capitulosContainer.addEventListener("click", function(event) {
            var target = event.target;
            // Botón de borrar capítulo
            if (target.closest(".deleteCapituloBtn")) {
                target.closest(".capitulo").remove();
            }
            // Botón de agregar partida (header o inline)
            if (target.closest(".addPartidaBtn") || target.closest(".addPartidaInlineBtn") || target.closest(".addPartidaHeaderBtn")) {
                var capDiv = target.closest(".capitulo");
                if (capDiv) {
                    var localIndex = capDiv.getAttribute("data-capitulo-index");
                    addPartida(localIndex, parseInt(localIndex) + 1);
                }
            }
            // Botón de borrar partida
            if (target.closest(".deletePartidaBtn")) {
                target.closest(".partida").remove();
            }
        });
    }
});
