class ApplicationController < ActionController::Base
  include Pundit
  protect_from_forgery with: :exception

  rescue_from Pundit::NotAuthorizedError do
    render file: "public/401.html", status: :unauthorized, layout: false
  end
end
