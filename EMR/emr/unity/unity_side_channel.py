
from asyncio import wait_for
import mlagents_envs as envs
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.side_channel import (
	SideChannel,
	IncomingMessage,
	OutgoingMessage,
)
import uuid

class CustomSideChannel(SideChannel):
	def __init__(self) -> None:
		super().__init__(uuid.UUID("621f0a70-4f87-11ea-a6bf-784f4387d1f7"))
		self.received_messages = []
		self.created_robot_module_keys = None
		self.wait_for_robot_string = True
		self.json_recording_of_individual = None

	def on_message_received(self, msg: IncomingMessage, debug : bool = True) -> None:
		message = msg.read_string()
		self.received_messages.append(message)
		if (debug):
			print(message)
		csvmes = message.split(",")
		if (csvmes[0] == "[Unity]:[Module Information]"):
			if (debug):
				print("[Python]:","received module information")
			csvmes.pop(0)
			self.created_robot_module_keys = csvmes
			self.wait_for_robot_string = False
		elif "[json recording]" in csvmes[0]:
			self.json_recording_of_individual = message[message.find(",")+1:]
			print("!!!!!!!!Received recording of an individual")
	def send_string(self,data: str, debug : bool = False) -> None:
		msg = OutgoingMessage()
		msg.write_string(data)
		if (debug):
			print(f"[Python]: sending {data}")
		super().queue_message_to_send(msg)
