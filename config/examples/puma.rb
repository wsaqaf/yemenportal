threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }.to_i
threads threads_count, threads_count

port ENV.fetch("API_PORT") { 3001 }

environment ENV.fetch("RAILS_ENV") { "development" }

plugin :tmp_restart
