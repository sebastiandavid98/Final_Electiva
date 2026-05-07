from rest_framework import permissions, serializers, viewsets

from accounts.models import Usuario

from .models import Reserva


class ReservaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id',
            'usuario',
            'laboratorio',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'motivo',
            'fecha_creacion',
        ]
        read_only_fields = ['estado', 'fecha_creacion']


class ReservaPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.rol == Usuario.ADMINISTRATIVO:
            return True
        return obj.usuario_id == user.id


class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated, ReservaPermission]

    def get_queryset(self):
        queryset = Reserva.objects.select_related('usuario')
        user = self.request.user
        if user.is_superuser or user.rol == Usuario.ADMINISTRATIVO:
            return queryset
        return queryset.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
