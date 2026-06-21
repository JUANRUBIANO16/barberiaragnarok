describe('CP-008 - Eliminar servicio sin citas asociadas', () => {

  it('Debe eliminar un servicio sin dependencias correctamente', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A SERVICIOS
    // ======================
    cy.visit('/servicios/');

    // ======================
    // ABRIR MODAL DELETE
    // ======================
    cy.get('a[href^="#deleteEmployeeModal"]')
      .first()
      .click({ force: true });

    // ======================
    // ESPERAR MODAL
    // ======================
    cy.get('.modal')
      .should('be.visible');

    // ======================
    // NOMBRE DEL SERVICIO (CAPTURAR PARA VALIDAR DESPUÉS)
    // ======================
    cy.get('.modal')
      .first()
      .invoke('text')
      .then((text) => {
        const nombreServicio = text;

        // ======================
        // CONFIRMAR ELIMINACIÓN
        // ======================
        cy.contains('Eliminar')
          .click({ force: true });

        // ======================
        // VALIDAR QUE YA NO EXISTE
        // ======================
        cy.contains(nombreServicio)
          .should('not.exist');
      });

  });

});