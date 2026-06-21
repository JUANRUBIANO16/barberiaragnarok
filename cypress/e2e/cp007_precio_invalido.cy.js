describe('CP-007 - Precio inválido en servicios', () => {

  it('Debe bloquear creación con precio inválido', () => {

    // LOGIN reutilizable
    cy.login();

    // ir módulo
    cy.visit('/servicios/');

    // abrir modal de forma estable (NO texto)
    cy.get('a[href="#addEmployeeModal"]')
      .should('exist')
      .click({ force: true });

    // asegurar modal abierto
    cy.get('#addEmployeeModal')
      .should('be.visible')
      .within(() => {

        cy.get('input[name="nombre"]')
          .type('Corte');

        cy.get('input[name="precio"]')
          .clear()
          .type('-67000');

        cy.get('textarea[name="descripcion"]')
          .type('Servicio inválido');

        cy.get('button')
          .contains('Guardar')
          .click();
      });

    // VALIDACIÓN REAL (Django messages)
    cy.get('.alert', { timeout: 10000 })
      .should('exist')
      .and('be.visible')
      .and('contain.text', 'precio');
  });

});