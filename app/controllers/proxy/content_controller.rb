class Proxy::ContentController < ApplicationController
  skip_before_action :verify_authenticity_token

  def show
    send_data proxied_content, type: content_type, disposition: :inline
  end

  private

  def proxied_content
    Net::HTTP.get(URI(params[:redirect_url]))
  end

  def content_type
    params[:type].presence || request.format
  end
end
