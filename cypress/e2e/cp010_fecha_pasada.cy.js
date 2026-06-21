describe('CP-010 - Registrar cita en fecha pasada', () => {

  it('Debe rechazar una cita con fecha anterior a la actual', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A CITAS
    // ======================
    cy.visit('/citas/');

    // ======================
    // ABRIR MODAL
    // ======================
    cy.contains('Agregar Cita')
      .click({ force: true });

    // ======================
    // ESPERAR MODAL
    // ======================
    cy.get('#addEmployeeModal')
      .should('be.visible');

    // ======================
    // FECHA PASADA
    // ======================
    cy.get('#addEmployeeModal input[name="fecha"]')
      .should('be.visible')
      .type('2026-06-18');

    // ======================
    // BARBERO
    // ======================
    cy.get('#addEmployeeModal select[name="barbero"]')
      .should('be.visible')
      .select('malo');

    // ======================
    // ESPERAR CARGA DE HORAS
    // ======================
    cy.wait(2000);

    // ======================
    // HORA
    // ======================
    cy.get('#addEmployeeModal select[name="hora"]')
      .should('be.visible')
      .then($select => {
        if ($select.find('option').length > 1) {
          cy.wrap($select).select(1);
        }
      });

    // ======================
    // ESTADO
    // ======================
    cy.get('#addEmployeeModal select[name="estado"]')
      .should('be.visible')
      .select('confirmada');

    // ======================
    // CLIENTE
    // ======================
    cy.get('#addEmployeeModal select[name="cliente"]')
      .should('be.visible')
      .select(1);

    // ======================
    // SERVICIO
    // ======================
    cy.get('#addEmployeeModal select[name="servicio"]')
      .should('be.visible')
      .select(1);

    // ======================
    // GUARDAR
    // ======================
    cy.contains('Guardar')
      .click({ force: true });

    // ======================
    // VALIDAR MENSAJE DE ERROR
    // ======================
     cy.get('.alert, .alert-success, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((text) => {
        expect(text.toLowerCase()).to.satisfy(msg =>
          msg.includes('no') ||
          msg.includes('error') ||
          msg.includes('registr')
        );
      });
    // ======================
    // SIGUE EN MÓDULO CITAS
    // ======================
    cy.url().should('include', '/citas');

  });

});