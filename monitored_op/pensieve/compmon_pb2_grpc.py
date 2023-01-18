# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import compmon_pb2 as compmon__pb2


class CompMonStub(object):
    """Component Monitoring Service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Report = channel.unary_unary(
                '/compmon.CompMon/Report',
                request_serializer=compmon__pb2.SARReport.SerializeToString,
                response_deserializer=compmon__pb2.ReportReply.FromString,
                )
        self.Register = channel.unary_unary(
                '/compmon.CompMon/Register',
                request_serializer=compmon__pb2.RegisterMessage.SerializeToString,
                response_deserializer=compmon__pb2.RegisterReply.FromString,
                )
        self.Finish = channel.unary_unary(
                '/compmon.CompMon/Finish',
                request_serializer=compmon__pb2.FinishMessage.SerializeToString,
                response_deserializer=compmon__pb2.FinishReply.FromString,
                )


class CompMonServicer(object):
    """Component Monitoring Service
    """

    def Report(self, request, context):
        """Send a State, Action, Reward Report to the server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Register(self, request, context):
        """Register/Reset or signal Compmon to allocate new logging arrays
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Finish(self, request, context):
        """Finished running - to be called by component on exit - to save all the logs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CompMonServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Report': grpc.unary_unary_rpc_method_handler(
                    servicer.Report,
                    request_deserializer=compmon__pb2.SARReport.FromString,
                    response_serializer=compmon__pb2.ReportReply.SerializeToString,
            ),
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=compmon__pb2.RegisterMessage.FromString,
                    response_serializer=compmon__pb2.RegisterReply.SerializeToString,
            ),
            'Finish': grpc.unary_unary_rpc_method_handler(
                    servicer.Finish,
                    request_deserializer=compmon__pb2.FinishMessage.FromString,
                    response_serializer=compmon__pb2.FinishReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'compmon.CompMon', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CompMon(object):
    """Component Monitoring Service
    """

    @staticmethod
    def Report(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/compmon.CompMon/Report',
            compmon__pb2.SARReport.SerializeToString,
            compmon__pb2.ReportReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/compmon.CompMon/Register',
            compmon__pb2.RegisterMessage.SerializeToString,
            compmon__pb2.RegisterReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Finish(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/compmon.CompMon/Finish',
            compmon__pb2.FinishMessage.SerializeToString,
            compmon__pb2.FinishReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
