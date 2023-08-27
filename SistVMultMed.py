from datetime import datetime
fecha_actual = datetime.now()
fecha_formateada = fecha_actual.strftime("%d de %B %Y")
class Medicamento:
    def __init__(self):
        self.__nombre = "" 
        self.__dosis = 0 
    
    def verNombre(self):
        return self.__nombre 
    def verDosis(self):
        return self.__dosis 
    
    def asignarNombre(self,med):
        self.__nombre = med 
    def asignarDosis(self,med):
        self.__dosis = med 

class Mascota:
    
    def __init__(self):
        self.__nombre= " "
        self.__historia=0
        self.__tipo=" "
        self.__peso=" "
        self.__fecha_ingreso=" "
        self.__lista_medicamentos=[]
        
    def verNombre(self):
        return self.__nombre
    def verHistoria(self):
        return self.__historia
    def verTipo(self):
        return self.__tipo
    def verPeso(self):
        return self.__peso
    def verFecha(self):
        return self.__fecha_ingreso
    def verLista_Medicamentos(self):
        return self.__lista_medicamentos
            
    def asignarNombre(self,n):
        self.__nombre=n
    def asignarHistoria(self,nh):
        self.__historia=nh
    def asignarTipo(self,t):
        self.__tipo=t
    def asignarPeso(self,p):
        self.__peso=p
    def asignarFecha(self,f):
        self.__fecha_ingreso=f
    def asignarMedicamento(self,n):
        self.__lista_medicamentos = n 
    
class sistemaV:
    def __init__(self):
        self.__lista_canino = {}
        self.__lista_felino={}
    
    def verificarExiste(self,m):
        if m in self.__lista_canino or m in self.__lista_felino:   
            return True
        return False
        
    def verNumeroMascotas(self):
        longitud=len(self.__lista_canino) + len(self.__lista_felino)
        return longitud
    
    def ingresarMascota(self,mascota,tipo):
        if tipo=="felino":
            self.__lista_felino[mascota.verHistoria()]=mascota
        if tipo=="canino":
            self.__lista_canino[mascota.verHistoria()]=mascota 
   

    def verFechaIngreso(self,historia):
        #busco la mascota y devuelvo el atributo solicitado
        for masc in self.__lista_felino:
            if historia == masc.verHistoria():
                return masc.verFecha()
        for masc in self.__lista_canino:
            if historia == masc.verHistoria():
                return masc.verFecha()
        return None

    def verMedicamento(self,historia):
        #busco la mascota y devuelvo el atributo solicitado
        for masc in self.__lista_canino:
            if historia == masc.verHistoria():
                return masc.verLista_Medicamentos() 
        for masc in self.__lista_felino:
            if historia == masc.verHistoria():
                return masc.verLista_Medicamentos() 
        return None
    
    def eliminarMedicamento(lista_med, nombre_medicamento):
     for medicamento in lista_med:
        if medicamento.verNombre() == nombre_medicamento:
            lista_med.remove(medicamento)
            print(f"Medicamento '{nombre_medicamento}' eliminado con éxito.")
            return
        print(f"No se encontró el medicamento '{nombre_medicamento}' en la lista.")
    
   
    
    def eliminarMascota(self, historia):
        for masc in self.__lista_canino:
            if historia == masc.verHistoria():
                self.__lista_canino.remove(masc)  #opcion con el pop
                return True  #eliminado con exito
        for masc in self.__lista_felino:
            if historia == masc.verHistoria():
                self.__lista_felino.remove(masc)  
                return True  
        return False 
    def agregarMedicamento(lista_med, nombre_medicamento, dosis):
     for m in lista_med:
        if m.verNombre() == nombre_medicamento:
            print("Este medicamento ya está en la lista. No se agregará nuevamente.")
            return
     medicamento = Medicamento()
     medicamento.asignarNombre(nombre_medicamento)
     medicamento.asignarDosis(dosis)
     lista_med.append(medicamento)

def main():
    servicio_hospitalario = sistemaV()
    # sistma=sistemaV()
    while True:
        menu=int(input('''\nIngrese una opción: 
                       \n1- Ingresar una mascota 
                       \n2- Ver fecha de ingreso 
                       \n3- Ver número de mascotas en el servicio 
                       \n4- Ver medicamentos que se están administrando
                       \n5- Eliminar mascota 
                       \n6- Eliminar medicamento
                       \n7- Salir 
                       \nUsted ingresó la opción: ''' ))
        if menu==1: # Ingresar una mascota 
            if servicio_hospitalario.verNumeroMascotas() >= 10:
                print("No hay espacio ...") 
                continue
            historia=int(input("Ingrese la historia clínica de la mascota: "))
            #   verificacion=servicio_hospitalario.verDatosPaciente(historia)
            if servicio_hospitalario.verificarExiste(historia) == False:
                nombre=input("Ingrese el nombre de la mascota: ")
                tipo=input("Ingrese el tipo de mascota (felino o canino): ")
                peso=int(input("Ingrese el peso de la mascota: "))
                fecha=str(fecha_formateada)
                nm=int(input("Ingrese cantidad de medicamentos: "))
                lista_med=[]

                for i in range(0,nm):
                    nombre_medicamento=input("Ingrese el nombre del medicamento: ")
                    dosis=int(input("ingrese la dosis del medicamento"))
                    agregarMedicamento(lista_med, nombre_medicamento, dosis)



                mas= Mascota()
                mas.asignarNombre(nombre)
                mas.asignarHistoria(historia)
                mas.asignarPeso(peso)
                mas.asignarTipo(tipo)
                mas.asignarFecha(fecha)
                mas.asignarLista_Medicamentos(lista_med)
                servicio_hospitalario.ingresarMascota(mas)

            else:
                print("Ya existe la mascota con el numero de histoira clinica")

        elif menu==2: # Ver fecha de ingreso
            q = int(input("Ingrese la historia clínica de la mascota: "))
            fecha = servicio_hospitalario.verFechaIngreso(q)
            # if servicio_hospitalario.verificarExiste == True
            if fecha != None:
                print("La fecha de ingreso de la mascota es: " + fecha)
            else:
                print("La historia clínica ingresada no corresponde con ninguna mascota en el sistema.")
            
        elif menu==3: # Ver número de mascotas en el servicio 
            numero=servicio_hospitalario.verNumeroMascotas()
            print("El número de pacientes en el sistema es: " + str(numero))

        elif menu==4: # Ver medicamentos que se están administrando
            q = int(input("Ingrese la historia clínica de la mascota: "))
            medicamento = servicio_hospitalario.verMedicamento(q) 
            if medicamento != None: 
                print("Los medicamentos suministrados son: ")
                for m in medicamento:   
                    print(f"\n- {m.verNombre()}")
            else:
                print("La historia clínica ingresada no corresponde con ninguna mascota en el sistema.")

        
        elif menu == 5: # Eliminar mascota
            q = int(input("Ingrese la historia clínica de la mascota: "))
            resultado_operacion = servicio_hospitalario.eliminarMascota(q) 
            if resultado_operacion == True:
                print("Mascota eliminada del sistema con exito")
            else:
                print("No se ha podido eliminar la mascota")
        elif menu==6: #eliminar medicamento
            q = int(input("Ingrese la historia clínica de la mascota: "))
            mascota = servicio_hospitalario.verMascota(q)
            if mascota:
              nombre_medicamento = input("Ingrese el nombre del medicamento a eliminar: ")
              eliminarMedicamento(mascota.verLista_Medicamentos(), nombre_medicamento)
            else:
              print("La historia clínica ingresada no corresponde con ninguna mascota en el sistema.")
        
        elif menu==7:
            print("Usted ha salido del sistema de servicio de hospitalización...")
            break
        
        else:
            print("Usted ingresó una opción no válida, intentelo nuevamente...")

if __name__=='__main__':
    main()





            

                

