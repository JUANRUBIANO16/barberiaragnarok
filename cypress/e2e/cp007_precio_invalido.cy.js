describe('CP-007 - Precio inválido en servicios', () => {

  it('Debe bloquear creación con precio inválido', () => {

    cy.login();

    cy.visit('/servicios/');

    // abrir modal SIN depender de texto
    cy.get('a[href="#addEmployeeModal"]')
      .should('exist')
      .click({ force: true });

    cy.get('#addEmployeeModal')
      .should('be.visible');

    cy.get('#addEmployeeModal input[name="nombre"]')
      .type('Corte');

    cy.get('#addEmployeeModal input[name="precio"]')
      .type('-67000');

    cy.get('#addEmployeeModal textarea[name="descripcion"]')
      .type('Test');

    cy.get('#addEmployeeModal button')
      .contains('Guardar')
      .click({ force: true });

    cy.get('.alert, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .and('contain.text', 'precio');

  });

});