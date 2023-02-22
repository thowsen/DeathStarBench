local _M = {}
local k8s_suffix = os.getenv("fqdn_suffix")
if (k8s_suffix == nil) then
  k8s_suffix = ""
end

local function _StrIsEmpty(s)
  return s == nil or s == ''
end

function dump(o)
   if type(o) == 'table' then
      local s = '{ '
      for k,v in pairs(o) do
         if type(k) ~= 'number' then k = '"'..k..'"' end
         s = s .. '['..k..'] = ' .. dump(v) .. ','
      end
      return s .. '} '
   else
      return tostring(o)
   end
end

function tablelength(T)
  local count = 0
  for _ in pairs(T) do count = count + 1 end
  return count
end


function _M.AddInstance() 
  local state = ngx.shared.state
  ngx.req.read_body()
  local new_instance = ngx.req.get_body_data()
  ngx.shared.state:set(new_instance, new_instance)
  ngx.say(dump(state:get_keys()))
end

function _M.RemoveInstance()
  local state = ngx.shared.state 
  ngx.req.read_body()
  local instance_to_be_removed = ngx.req.get_body_data()
  state:delete(instance_to_be_removed)
  ngx.say(dump(state:get_keys()))
end 

function _M.RegisterUser()
  local bridge_tracer = require "opentracing_bridge_tracer"
  local cjson = require "cjson"
  local ngx = ngx
  local state = ngx.shared.state
  local round_robin = ngx.shared.round_robin
  local GenericObjectPool = require "GenericObjectPool"
  local social_network_UserService = require "social_network_UserService"
  local UserServiceClient = social_network_UserService.UserServiceClient
  ngx.req.read_body()
  local body_json = cjson.decode(ngx.req.get_body_data())
  local intra_service_communication_on = body_json["intra_service"]
  if intra_service_communication_on == nil then 
    intra_service_communication_on = 0
  end

  local intra_service_instances= body_json["intra_service_instances"]
  if intra_service_instances == nil then 
    intra_service_instances = ""
  end

  local work_duration = body_json["work_duration"]
  if work_duration == nil then 
    work_duration = "0"
  end

  local req_id = tonumber(string.sub(ngx.var.request_id, 0, 15), 16)
  local tracer = bridge_tracer.new_from_global()
  local parent_span_context = tracer:binary_extract(
      ngx.var.opentracing_binary_context)
  local span = tracer:start_span("register_client",
      {["references"] = {{"child_of", parent_span_context}}})
  local carrier = {}
  tracer:text_map_inject(span:context(), carrier)

  ngx.req.read_body()
  local post = ngx.req.get_post_args()

  local curr = round_robin:get("value")
  if curr == nil then 
    curr = 0
  end 
  local keys = state:get_keys()
  local round_robin_instance = keys[curr % tablelength(keys) + 1]

  round_robin:set("value", curr + 1)

  local remove_index = nil 
  local out_instances = {}
  local out_string = ""
  for k, v in pairs(state:get_keys()) do 
    if v ~= round_robin_instance then 
      local v2 = v .. k8s_suffix .. ","
      out_string = out_string .. v2 
      table.insert(out_instances, v2)
    end 
  end 
  out_string = out_string:sub(1, -2)


  --if (_StrIsEmpty(post.first_name) or _StrIsEmpty(post.last_name) or
  --    _StrIsEmpty(post.username) or _StrIsEmpty(post.password) or
  --    _StrIsEmpty(post.user_id)) then
  --  ngx.status = ngx.HTTP_BAD_REQUEST
  --  ngx.say("Incomplete arguments")
  --  ngx.log(ngx.ERR, "Incomplete arguments")
  --  ngx.exit(ngx.HTTP_BAD_REQUEST)
  --end

  local client = GenericObjectPool:connection(UserServiceClient, "user-service" .. round_robin_instance ..k8s_suffix, 9090)
  local status, err = pcall(client.RegisterUserWithId, client, req_id, "aaaaaaa",
      work_duration, intra_service_instances, out_string, intra_service_communication_on, carrier)
  if not status then
    ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
    if (err.message) then
      ngx.say("User registration failure: " .. err.message)
      ngx.log(ngx.ERR, "User registration failure: " .. err.message)
    else
      ngx.say("User registration failure: " .. err)
      ngx.log(ngx.ERR, "User registration failure: " .. err)
    end
    client.iprot.trans:close()
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
  end
  if err then 
    ngx.say("oh noes")
    client.iprot.trans:close()
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
  end
  ngx.say(round_robin_instance)
  GenericObjectPool:returnConnection(client)
  span:finish()
end

return _M