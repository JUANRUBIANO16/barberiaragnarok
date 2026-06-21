describe('CP-007 - Validar precio inválido en creación de servicios', () => {

  it('Debe rechazar servicios con precio negativo o vacío', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A SERVICIOS
    // ======================
    cy.visit('/servicios/');

    // ======================
    // ABRIR MODAL
    // ======================
    cy.contains('Agregar Servicios')
      .click({ force: true });

    // ======================
    // ESPERAR MODAL LISTO
    // ======================
    cy.get('#addEmployeeModal')
      .should('be.visible');

    // ======================
    // LLENAR FORMULARIO (INVALIDO)
    // ======================
    cy.get('#addEmployeeModal input[name="nombre"]')
      .should('be.visible')
      .type('Corte test');

    cy.get('#addEmployeeModal input[name="precio"]')
      .should('be.visible')
      .clear()
      .type('-67000');   // ❌ precio inválido

    cy.get('#addEmployeeModal textarea[name="descripcion"]')
      .should('be.visible')
      .type('Prueba Cypress');

    // ======================
    // GUARDAR
    // ======================
    cy.contains('Guardar')
      .click({ force: true });

    // ======================
    // VALIDAR ERROR
    // ======================
    cy.get('.alert, .error, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((text) => {
        expect(text.toLowerCase()).to.satisfy(msg =>
          msg.includes('precio') ||
          msg.includes('inválido') ||
          msg.includes('error')
        );
      });

  });

});