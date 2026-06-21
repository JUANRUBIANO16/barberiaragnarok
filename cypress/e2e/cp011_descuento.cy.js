describe('CP-011 - Aplicación automática de descuento', () => {

  it('Debe calcular automáticamente el descuento según el subtotal', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A VENTAS
    // ======================
    cy.visit('/venta/');

    // ======================
    // ABRIR MODAL
    // ======================
    cy.contains('Agregar Venta')
      .click({ force: true });

    // ======================
    // ESPERAR MODAL
    // ======================
    cy.get('#addModal')
      .should('be.visible');

    // ======================
    // SELECCIONAR CITA
    // ======================
    cy.get('#citaSelect')
      .should('be.visible')
      .select(1);

    // ======================
    // VALIDAR SUBTOTAL
    // ======================
    cy.get('#subtotalPreview')
      .should('be.visible')
      .invoke('val')
      .then((subtotal) => {

        const valor = Number(subtotal);

        expect(valor).to.be.greaterThan(0);

        // ======================
        // VALIDAR DESCUENTO
        // ======================
        cy.get('#descuentoPreview')
          .invoke('val')
          .then((descuento) => {

            const desc = Number(descuento);

            if (valor >= 150000) {
              expect(desc).to.equal(valor * 0.15);
            } else if (valor >= 100000) {
              expect(desc).to.equal(valor * 0.10);
            } else if (valor >= 50000) {
              expect(desc).to.equal(valor * 0.05);
            } else {
              expect(desc).to.equal(0);
            }
          });
      });

    // ======================
    // GUARDAR
    // ======================
    cy.contains('Guardar')
      .click({ force: true });

    // ======================
    // VALIDACIÓN
    // ======================
    cy.get('.alert, .alert-success, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((text) => {
        expect(text.toLowerCase()).to.satisfy(msg =>
          msg.includes('venta') ||
          msg.includes('registr') ||
          msg.includes('exit')
        );
      });

  });

});