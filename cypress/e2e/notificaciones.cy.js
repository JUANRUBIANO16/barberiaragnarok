describe('CP-013 - Aceptar solicitud y convertir en cita', () => {

  it('Debe aceptar una solicitud pendiente y convertirla en cita', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A NOTIFICACIONES
    // ======================
    cy.visit('/notificaciones/');

    // ======================
    // ABRIR SOLICITUD PENDIENTE
    // ======================
    cy.get('i.text-success')
      .first()
      .click({ force: true });

    // ======================
    // ESPERAR MODAL
    // ======================
    cy.get('.modal.show')
      .should('be.visible');

    // ======================
    // FECHA
    // ======================
    cy.get('.modal.show input[name="fecha"]')
      .should('be.visible')
      .type('2026-06-25');

    // ======================
    // BARBERO
    // ======================
    cy.get('.modal.show select[name="barbero"]')
      .should('be.visible')
      .select('malo');

    // ======================
    // ESPERAR HORAS DINÁMICAS
    // ======================
    cy.wait(2000);

    cy.get('.modal.show select[name="hora"]')
      .should('be.visible')
      .then($select => {
        if ($select.find('option').length > 1) {
          cy.wrap($select).select(1);
        }
      });

    // ======================
    // SERVICIO
    // ======================
    cy.get('.modal.show select[name="servicio"]')
      .should('be.visible')
      .select(1);

    // ======================
    // CONFIRMAR (FIX REAL)
    // ======================
    cy.get('.modal.show')
      .within(() => {
        cy.get('button.btn-success')
          .contains('Confirmar')
          .should('be.visible')
          .click();
      });

    // ======================
    // VALIDACIÓN FINAL (SIN ALERTS)
    // ======================
    cy.get('body')
      .should('contain.text', 'Aceptada');

  });

});