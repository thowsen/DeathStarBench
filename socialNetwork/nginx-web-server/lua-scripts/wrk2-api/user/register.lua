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
  ngx.req.read_body()
  local instance_to_be_removed = ngx.req.get_body_data()
  local state = ngx.shared.state 
  state:delete(instance_to_be_removed)
  ngx.say(dump(state:get_keys()))
end 

function _M.RegisterUser()
  local bridge_tracer = require "opentracing_bridge_tracer"
  local ngx = ngx
  local state = ngx.shared.state
  local round_robin = ngx.shared.round_robin
  local GenericObjectPool = require "GenericObjectPool"
  local social_network_UserService = require "social_network_UserService"
  local UserServiceClient = social_network_UserService.UserServiceClient

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

  ngx.log(ngx.ERR, "instance being accessed is: \t ", round_robin_instance)
  round_robin:set("value", curr + 1)

  --if (_StrIsEmpty(post.first_name) or _StrIsEmpty(post.last_name) or
  --    _StrIsEmpty(post.username) or _StrIsEmpty(post.password) or
  --    _StrIsEmpty(post.user_id)) then
  --  ngx.status = ngx.HTTP_BAD_REQUEST
  --  ngx.say("Incomplete arguments")
  --  ngx.log(ngx.ERR, "Incomplete arguments")
  --  ngx.exit(ngx.HTTP_BAD_REQUEST)
  --end

  local client = GenericObjectPool:connection(UserServiceClient, "user-service" .. round_robin_instance ..k8s_suffix, 9090)

  local status, err = pcall(client.RegisterUserWithId, client, req_id, post.first_name,
      post.last_name, post.username, post.password, tonumber(post.user_id), carrier)
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

  ngx.say("Success! " .. k8s_suffix)
  ngx.log(ngx.ERR,"Success! " .. k8s_suffix)
  GenericObjectPool:returnConnection(client)
  span:finish()
end

return _M