describe('CP-009 - Creación exitosa de cita', () => {

  it('Debe registrar una cita correctamente', () => {

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
    // FECHA
    // ======================
    cy.get('#addEmployeeModal input[name="fecha"]')
      .should('be.visible')
      .type('2026-06-22');

    // ======================
    // BARBERO
    // ======================
    cy.get('#addEmployeeModal select[name="barbero"]')
      .should('be.visible')
      .select("malo");

    // ======================
    // HORA (depende de fetch dinámico)
    // ======================
    cy.wait(2000);

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
    // VALIDACIÓN
    // ======================
    cy.get('.alert, .alert-success, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((text) => {
        expect(text.toLowerCase()).to.satisfy(msg =>
          msg.includes('cre') ||
          msg.includes('exit') ||
          msg.includes('registr')
        );
      });

  });

});