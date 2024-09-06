CREATE OR REPLACE TRIGGER SGCPESYS.TRI_MENU BEFORE
--*************************************************************************************************
-- Nombre:      TRI_MENU
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_MENU
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_MENU
    FOR EACH ROW
     WHEN ( NEW.N_IDMENU IS NULL ) BEGIN
    :NEW.N_IDMENU := SGCPESYS.SEQ_GCPEMEN.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_MENU ENABLE;


CREATE OR REPLACE TRIGGER SGCPESYS.TRI_GRUPERMISO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_GRUPERMISO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_GRUMEN
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_GRUMEN
    FOR EACH ROW
     WHEN ( NEW.N_IDGRUMEN IS NULL ) BEGIN
    :NEW.N_IDGRUMEN := SGCPESYS.SEQ_GCPEGRUPER.NEXTVAL;
END;
/
ALTER TRIGGER SGCPESYS.TRI_GRUPERMISO ENABLE;

CREATE OR REPLACE TRIGGER SGCPESYS.TRI_PARAMETRO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_PARAMETRO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_PARAMETRO
--*************************************************************************************************

    INSERT ON SGCPESYS.GCPETBX_PARAMETRO
    FOR EACH ROW
     WHEN ( NEW.N_IDPARAMETRO IS NULL ) BEGIN
    :NEW.N_IDPARAMETRO := SGCPESYS.SEQ_GCPEPAR.NEXTVAL;
END;
/
ALTER TRIGGER SGCPESYS.TRI_PARAMETRO ENABLE;

CREATE OR REPLACE TRIGGER SGCPESYS.TRI_PERMISO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_PERMISO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_PERMISO
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_PERMISO
    FOR EACH ROW
     WHEN ( NEW.N_IDPERMISO IS NULL ) BEGIN
    :NEW.N_IDPERMISO := SGCPESYS.SEQ_GCPEPER.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_PERMISO ENABLE;

CREATE OR REPLACE TRIGGER SGCPESYS.TRI_USUARIO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_USUARIO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_USUARIO
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_USUARIO
    FOR EACH ROW
     WHEN ( NEW.N_IDUSUARIO IS NULL ) BEGIN
    :NEW.N_IDUSUARIO := SGCPESYS.SEQ_GCPEUSU.NEXTVAL;
END;
/
ALTER TRIGGER SGCPESYS.TRI_USUARIO ENABLE;



CREATE OR REPLACE TRIGGER SGCPESYS.TRI_REGLA BEFORE
--*************************************************************************************************
-- Nombre:      TRI_REGLA
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_REGLA
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_REGLA
    FOR EACH ROW
     WHEN ( NEW.N_IDREGLA IS NULL ) BEGIN
    :NEW.N_IDREGLA := SGCPESYS.SEQ_GCPEREGLA.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_REGLA ENABLE;


CREATE OR REPLACE TRIGGER SGCPESYS.TRI_USUGRUPO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_USUGRUPO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_USUGRU
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_USUGRU
    FOR EACH ROW
     WHEN ( NEW.N_IDUSUGRU IS NULL ) BEGIN
    :NEW.N_IDUSUGRU := SGCPESYS.SEQ_GCPEUSUGRU.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_USUGRUPO ENABLE;


CREATE OR REPLACE TRIGGER SGCPESYS.TRI_MOTIVO BEFORE
--*************************************************************************************************
-- Nombre:      TRI_MOTIVO
-- Sistema:     SCALVIR
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPETBX_MOTIVO
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPETBX_MOTIVO
    FOR EACH ROW
     WHEN ( NEW.N_IDMOTIVO IS NULL ) BEGIN
    :NEW.N_IDMOTIVO := SGCPESYS.SEQ_GCPEMOTIVO.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_MOTIVO ENABLE;

CREATE OR REPLACE TRIGGER SGCPESYS.TRI_SOLICITUD BEFORE
--*************************************************************************************************
-- Nombre:      TRI_SOLICITUD
-- Sistema:     GCE PLANILLAS
-- Autor:       Omar Ruelas Principe - Fecha de Creacion: 10-05-2023
-- Modificador: Fecha de Modificacion: 10-05-2023
-- Objetivo:    PAQUETE PARA TRIGGER DE TABLA SGCPESYS.GCPEMVC_SOLICITUD
--*************************************************************************************************
    INSERT ON SGCPESYS.GCPEMVC_SOLICITUD
    FOR EACH ROW
     WHEN ( NEW.N_IDSOLICITUD IS NULL ) BEGIN
    :NEW.N_IDSOLICITUD := SGCPESYS.SEQ_GCPESOLICITUD.NEXTVAL;
END;

/
ALTER TRIGGER SGCPESYS.TRI_SOLICITUD ENABLE;
