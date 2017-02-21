require "rails_helper"

describe SourcesController, type: :request do
  describe "#new" do
    let(:do_request) { get "/sources/new" }

    it "show a main page" do
      do_request
      expect(response).to be_success
    end
  end

  describe "#create" do
    let(:params) { { source: { link: "www.as@mail.com" } } }
    let(:do_request) { post "/sources", params: params }

    context "seccess reques" do
      it "redirect to sources list" do
        do_request
        expect(response.status).to eq 302
        expect(response).to redirect_to(sources_path)
      end
    end

    context "fail request" do
      let(:params) { { source: { link: nil } } }

      it "redirect to create form" do
        do_request
        expect(response.status).to eq 200
        expect(response).not_to redirect_to(sources_path)
      end
    end
  end

  describe "#destroy" do
    let(:source) { create :source }
    let(:do_request) { delete "/sources/#{source.id}" }

    it "redirect to sources list" do
      do_request
      expect(response.status).to eq 302
      expect(response).to redirect_to(sources_path)
    end
  end

  describe "#index" do
    let(:do_request) { get "/sources" }

    it "redirect to sources list" do
      do_request
      expect(response.status).to eq 200
    end
  end
end
