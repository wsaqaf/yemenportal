require "rails_helper"
include ActiveJob::TestHelper

describe SourcesController, type: :request do
  let(:user) { build :user, role: :admin }

  describe "#new" do
    let(:do_request) { get "/sources/new" }

    it "show a main page" do
      sign_in user
      do_request

      expect(response).to be_success
    end
  end

  describe "#create" do
    let(:params) { { source: { link: "http://asmail.com", website: "http://asmail.com", name: "some_name" } } }
    let(:do_request) { post "/sources", params: params }

    context "success reques" do
      it "redirect to sources list" do
        sign_in user
        do_request

        expect(response.status).to eq 302
        expect(response).to redirect_to(sources_path(approve_state: Source.approve_state.approved))
      end
    end

    context "fail request" do
      let(:params) { { source: { link: nil } } }

      it "redirect to create form" do
        sign_in user
        do_request

        expect(response.status).to eq 200
        expect(response).not_to redirect_to(sources_path)
      end
    end
  end

  describe "#edit" do
    let(:source) { create :source }
    let(:do_request) { get "/sources/#{source.id}/edit" }

    it "source" do
      sign_in user
      do_request

      expect(response).to be_success
    end
  end

  describe "#update" do
    let(:source) { create :source }
    let(:posts_fetcher_job) { double }
    let(:do_request) do
      put "/sources/#{source.id}", params: { source: { link: "http://ddd1234.com", category_id: source.category_id,
        whitelisted: "true" } }
    end
    let(:do_bad_request) do
      put "/sources/#{source.id}", params: { source: { link: "", category_id: source.category_id } }
    end

    it "source params" do
      sign_in user
      stub_const("PostsFetcherJob", posts_fetcher_job)
      allow(posts_fetcher_job).to receive(:perform_later) { true }

      do_request
      expect(response).to redirect_to(sources_path(approve_state: Source.approve_state.approved))
    end

    it "source fails" do
      sign_in user
      do_bad_request

      expect(response.status).to eq 200
      expect(response).not_to redirect_to(sources_path)
    end
  end

  describe "#destroy" do
    let(:source) { create :source }
    let(:do_request) { delete "/sources/#{source.id}" }

    it "source" do
      sign_in user
      do_request

      expect(response).to redirect_to(sources_path(approve_state: Source.approve_state.approved))
    end
  end

  describe "#destroy" do
    let(:source) { create :source }
    let(:do_request) { delete "/sources/#{source.id}" }

    it "redirect to sources list" do
      sign_in user
      do_request

      expect(response.status).to eq 302
      expect(response).to redirect_to(sources_path(approve_state: Source.approve_state.approved))
    end
  end

  describe "#index" do
    let(:do_request) { get "/sources", params: { approve_state: "approved" } }

    it "redirect to sources list" do
      sign_in user
      do_request

      expect(response.status).to eq 200
    end
  end
end
