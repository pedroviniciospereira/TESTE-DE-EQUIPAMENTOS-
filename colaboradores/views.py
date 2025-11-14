# Importações necessárias do Django
# ================================
from django.shortcuts import render, redirect, get_object_or_404 
from .models import Colaborador, messages
from .forms import ColaboradorForm , reverse# <--- 1. IMPORTAMOS O SEU NOVO FORM
from django.db.models import Q ,Equipamento
from django.contrib import messages, EquipamentoForm

def cadastro_equipamento(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento cadastrado com sucesso.")
            return redirect('equipamentos:cadastro')  # permanece na tela após cadastro
        else:
            messages.error(request, "Falha ao cadastrar equipamento. Verifique os dados.")
    else:
        form = EquipamentoForm()
    return render(request, 'equipamentos/cadastro.html', {'form': form})

def lista_equipamentos(request):
    equipamentos = Equipamento.objects.all().order_by('-id')
    return render(request, 'equipamentos/lista.html', {'equipamentos': equipamentos})

def editar_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento atualizado com sucesso.")
            return redirect('equipamentos:lista')
        else:
            messages.error(request, "Falha ao atualizar. Verifique os dados.")
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'equipamentos/editar.html', {'form': form, 'equipamento': equipamento})

def excluir_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        equipamento.delete()
        messages.success(request, "Equipamento excluído com sucesso.")
        return redirect('equipamentos:lista')
    # Em caso de GET, redireciona para lista (a confirmação será via modal/JS)
    return redirect('equipamentos:lista') View (Função) para a página de LISTA de Colaboradores (index.html)
# =================================================================
def colaborador_lista(request):
    query = request.GET.get('q', '')
    
    if query:
        colaboradores = Colaborador.objects.filter(
            Q(nome_completo__icontains=query) |
            Q(matricula__icontains=query) | # <- Corrigido de 'cpf' para 'matricula'
            Q(funcao__icontains=query)
        ).order_by('-data_cadastro')
    else:
        colaboradores = Colaborador.objects.all().order_by('-data_cadastro')
    
    total_colaboradores = colaboradores.count()
    colaboradores_ativos = colaboradores.filter(status='Ativo').count()
    colaboradores_inativos = total_colaboradores - colaboradores_ativos

    context = {
        'colaboradores_lista': colaboradores,
        'total_colaboradores': total_colaboradores,
        'colaboradores_ativos': colaboradores_ativos,
        'colaboradores_inativos': colaboradores_inativos,
        'search_query': query 
    }
    return render(request, 'index.html', context)


# View (Função) para a página de CADASTRO de Colaboradores (cadastro.html)
# ======================================================================
def colaborador_novo(request):
    if request.method == 'POST':
        # 2. Criamos o form passando os dados do POST
        form = ColaboradorForm(request.POST)
        
        # 3. O form.is_valid() VAI CHAMAR O SEU 'clean_matricula'
        if form.is_valid():
            # Se for válido (não é duplicado, é só número), salvamos
            form.save()
            messages.success(request, 'Colaborador cadastrado com sucesso!')
            form_vazio = ColaboradorForm() 
            return render(request, 'cadastro.html', {'form': form_vazio})
        # Se for INVÁLIDO (duplicado, etc.), o Django vai adicionar
        # os erros ao 'form' e continuar para o 'render' abaixo
    
    else:
        # 4. Se for GET, apenas criamos um form vazio
        form = ColaboradorForm()

    # 5. Renderizamos o template passando o 'form'
    #    (O form estará vazio ou conterá os erros e os dados que o usuário digitou)
    return render(request, 'cadastro.html', {'form': form})


# View (Função) para a página de EDIÇÃO de Colaboradores (reutiliza cadastro.html)
# ==============================================================================
def colaborador_editar(request, id):
    # Buscamos o colaborador que queremos editar
    colaborador = get_object_or_404(Colaborador, id=id)

    if request.method == 'POST':
        # 6. Criamos o form passando os dados do POST E a 'instance'
        #    (Isso diz ao form que estamos EDITANDO)
        form = ColaboradorForm(request.POST, instance=colaborador)
        
        # 7. O 'clean_matricula' vai rodar e excluir o próprio
        #    colaborador da checagem de duplicidade
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador atualizado com sucesso!')
            return redirect('index')
        # Se for inválido, continua para o 'render'
    
    else:
        # 8. Se for GET, criamos o form preenchido com os dados da 'instance'
        form = ColaboradorForm(instance=colaborador)

    # 9. Renderizamos o template com o form (preenchido ou com erros)
    #    E também passamos o 'colaborador' para o template saber que é modo "Editar"
    context = {
        'form': form,
        'colaborador': colaborador 
    }
    return render(request, 'cadastro.html', context)


# View (Função) para EXCLUIR um Colaborador
# =========================================
def colaborador_excluir(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    
    # 10. (Importante) Protegemos a exclusão para aceitar apenas POST
    if request.method == 'POST':
        nome_colaborador = colaborador.nome_completo
        colaborador.delete()
        messages.success(request, f'Colaborador "{nome_colaborador}" foi excluído.')
    
    # Redireciona para a lista (se for GET, apenas redireciona sem excluir)
    return redirect('index')